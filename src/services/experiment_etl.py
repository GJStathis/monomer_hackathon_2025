import csv
import re
from pathlib import Path
from typing import Dict, Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.repositories.experiment_repository import ExperimentRepository
from src.repositories.reagent_value_repository import ReagentValueRepository
from src.repositories.reagent_repository import ReagentRepository


class ExperimentETL:
    """ETL script to ingest experiment data from CSV files"""
    
    # Special row identifiers for experiment parameters
    CELL_CONCENTRATION_KEY = "cell concentration"
    DILUTION_KEY = "dilution"
    
    def __init__(self, database_url: str = "sqlite:///./database.db"):
        """Initialize ETL with database connection"""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @staticmethod
    def parse_experiment_id_from_filename(filename: str) -> Optional[int]:
        """
        Parse experiment ID from filename pattern: *exp {id}*.csv
        
        Example: "Costs analysis of chemicals - exp 1.csv" -> 1
        """
        match = re.search(r'exp\s+(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def parse_csv_file(self, file_path: Path) -> Dict:
        """
        Parse CSV file and extract experiment data.
        
        The CSV format has:
        - Header row: type, value, Units
        - Row 2: cell concentration, <value>, <empty>
        - Row 3: dilution, <value>, <empty>
        - Remaining rows: <reagent_name>, <value>, <unit>
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            Dictionary containing:
                - experiment_id: int (from filename)
                - cell_concentration: float
                - dilution: float
                - reagent_values: list of dicts with reagent_name, value, unit
        """
        # Extract experiment_id from filename
        experiment_id = self.parse_experiment_id_from_filename(file_path.name)
        if experiment_id is None:
            raise ValueError(f"Could not parse experiment ID from filename: {file_path.name}")
        
        experiment_data = {
            'experiment_id': experiment_id,
            'cell_concentration': None,
            'dilution': None,
            'reagent_values': []
        }
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                row_type = row['type'].strip().lower()
                value_str = row['value'].strip()
                unit = row.get('Units', '').strip() if 'Units' in row else ''
                
                # Skip empty rows
                if not row_type or not value_str:
                    continue
                
                try:
                    value = float(value_str)
                except ValueError:
                    print(f"Warning: Skipping row with non-numeric value: {row_type} = {value_str}")
                    continue
                
                # Extract experiment parameters
                if row_type == self.CELL_CONCENTRATION_KEY:
                    experiment_data['cell_concentration'] = value
                elif row_type == self.DILUTION_KEY:
                    experiment_data['dilution'] = value
                else:
                    # This is a reagent value
                    experiment_data['reagent_values'].append({
                        'reagent_name': row['type'].strip(),
                        'value': value,
                        'unit': unit
                    })
        
        # Validate required fields
        if experiment_data['cell_concentration'] is None:
            raise ValueError(f"Missing cell concentration in {file_path.name}")
        if experiment_data['dilution'] is None:
            raise ValueError(f"Missing dilution in {file_path.name}")
        
        return experiment_data
    
    def ingest_file(self, file_path: Path) -> int:
        """
        Ingest a single CSV file into the database.
        
        Creates:
        1. One Experiment record
        2. Multiple ReagentValue records (one per reagent)
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            Experiment ID
        """
        # Parse the CSV file
        experiment_data = self.parse_csv_file(file_path)
        
        # Start database session
        session = self.SessionLocal()
        try:
            # Create repositories
            experiment_repo = ExperimentRepository(session)
            reagent_value_repo = ReagentValueRepository(session)
            reagent_repo = ReagentRepository(session)
            
            # Create experiment record
            experiment = experiment_repo.create(
                cell_concentration=experiment_data['cell_concentration'],
                dilution=experiment_data['dilution']
            )
            
            print(f"Created experiment {experiment.id} with:")
            print(f"  - Cell concentration: {experiment.cell_concentration}")
            print(f"  - Dilution: {experiment.dilution}")
            
            # Create reagent value records
            reagent_values_to_insert = []
            skipped_reagents = []
            
            for rv_data in experiment_data['reagent_values']:
                # Look up reagent by name
                reagent = reagent_repo.get_by_name(rv_data['reagent_name'])
                
                if reagent:
                    reagent_values_to_insert.append({
                        'experiment_id': experiment.id,
                        'reagent_id': reagent.id,
                        'value': rv_data['value'],
                        'unit': rv_data['unit']
                    })
                else:
                    skipped_reagents.append(rv_data['reagent_name'])
            
            # Bulk insert reagent values
            if reagent_values_to_insert:
                count = reagent_value_repo.bulk_create(reagent_values_to_insert)
                print(f"  - Inserted {count} reagent values")
            
            if skipped_reagents:
                print(f"  - Skipped {len(skipped_reagents)} reagents not found in database:")
                for reagent_name in skipped_reagents:
                    print(f"    * {reagent_name}")
            
            print(f"\nSuccessfully ingested experiment from {file_path.name}")
            return experiment.id
            
        except Exception as e:
            session.rollback()
            print(f"Error ingesting data from {file_path.name}: {e}")
            raise
        finally:
            session.close()
    
    def ingest_directory(self, directory_path: Path, pattern: str = "*exp*.csv") -> List[int]:
        """
        Ingest all matching CSV files from a directory.
        
        Args:
            directory_path: Path to directory containing CSV files
            pattern: Glob pattern for matching files
        
        Returns:
            List of experiment IDs created
        """
        experiment_ids = []
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                try:
                    experiment_id = self.ingest_file(file_path)
                    experiment_ids.append(experiment_id)
                except Exception as e:
                    print(f"Failed to process {file_path.name}: {e}")
                    continue
        
        print(f"\nTotal experiments created: {len(experiment_ids)}")
        return experiment_ids


def main():
    """Example usage of the ETL script"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.services.experiment_etl <file_or_directory_path>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    etl = ExperimentETL()
    
    if input_path.is_file():
        etl.ingest_file(input_path)
    elif input_path.is_dir():
        etl.ingest_directory(input_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()

