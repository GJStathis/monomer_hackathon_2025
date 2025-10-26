import csv
import re
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.repositories.plate_repository import PlateRepository


class AbsorbanceETL:
    """ETL script to ingest absorbance plate data from CSV files"""
    
    def __init__(self, database_url: str = "sqlite:///./database.db"):
        """Initialize ETL with database connection"""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @staticmethod
    def parse_plate_id_from_filename(filename: str) -> Optional[int]:
        """
        Parse plate_id from filename pattern: plate_{id}_*.csv
        
        Example: plate_1_abs.csv -> 1
        """
        match = re.search(r'plate_(\d+)', filename)
        if match:
            return int(match.group(1))
        return None
    
    @staticmethod
    def parse_well_identifier(well_str: str) -> tuple[str, int]:
        """
        Parse well identifier into row_id and column_id.
        
        Example: "A1" -> ("A", 1), "H12" -> ("H", 12)
        
        Args:
            well_str: Well identifier like "A1", "B3", "H12"
        
        Returns:
            Tuple of (row_id, column_id)
        """
        match = re.match(r'([A-H])(\d+)', well_str)
        if match:
            row_id = match.group(1)
            column_id = int(match.group(2))
            return (row_id, column_id)
        raise ValueError(f"Invalid well identifier: {well_str}")
    
    def parse_csv_file(self, file_path: Path) -> List[Dict]:
        """
        Parse CSV file and extract plate data.
        
        The CSV format has:
        - Row 1: Header with well identifiers (A1, A2, ..., H12)
        - Subsequent rows: First column is time in seconds, remaining columns are absorbance values
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            List of dictionaries containing plate_id, row_id, column_id, value, and seconds_time_sample
        """
        # Extract plate_id from filename
        plate_id = self.parse_plate_id_from_filename(file_path.name)
        if plate_id is None:
            raise ValueError(f"Could not parse plate_id from filename: {file_path.name}")
        
        plate_data = []
        
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            
            if len(rows) < 2:
                raise ValueError(f"CSV file has fewer than 2 rows: {file_path.name}")
            
            # Parse header row (row 0) to get well identifiers
            header = rows[0]
            well_identifiers = []
            
            # Skip first column (empty or time label), parse remaining columns
            for col_idx in range(1, len(header)):
                well_str = header[col_idx].strip()
                if well_str:  # Only process non-empty headers
                    try:
                        row_id, column_id = self.parse_well_identifier(well_str)
                        well_identifiers.append((col_idx, row_id, column_id))
                    except ValueError:
                        # Skip invalid well identifiers
                        continue
            
            # Process data rows
            # Stop when we hit empty rows or rows that don't start with a number
            for row_idx in range(1, len(rows)):
                row = rows[row_idx]
                
                # Skip empty rows or rows without time data
                if not row or not row[0].strip():
                    continue
                
                # Try to parse the first column as time (seconds)
                try:
                    seconds_time_sample = int(float(row[0].strip()))
                except (ValueError, IndexError):
                    # Stop processing when we hit non-numeric time values
                    break
                
                # Process each well's absorbance value
                for col_idx, row_id, column_id in well_identifiers:
                    if col_idx < len(row):
                        value_str = row[col_idx].strip()
                        
                        # Skip empty values
                        if value_str:
                            try:
                                value = float(value_str)
                                
                                plate_data.append({
                                    'plate_id': plate_id,
                                    'row_id': row_id,
                                    'column_id': column_id,
                                    'value': value,
                                    'seconds_time_sample': seconds_time_sample
                                })
                            except ValueError:
                                # Skip non-numeric values
                                print(f"Warning: Skipping non-numeric value at row {row_idx}, col {col_idx}: {value_str}")
                                continue
        
        return plate_data
    
    def ingest_file(self, file_path: Path) -> int:
        """
        Ingest a single CSV file into the database.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            Number of records inserted
        """
        # Parse the CSV file
        plate_data = self.parse_csv_file(file_path)
        
        if not plate_data:
            print(f"No data to insert from {file_path.name}")
            return 0
        
        # Insert into database
        session = self.SessionLocal()
        try:
            repo = PlateRepository(session)
            count = repo.bulk_create(plate_data)
            print(f"Successfully inserted {count} records from {file_path.name}")
            return count
        except Exception as e:
            session.rollback()
            print(f"Error inserting data from {file_path.name}: {e}")
            raise
        finally:
            session.close()
    
    def ingest_directory(self, directory_path: Path, pattern: str = "plate_*_abs.csv") -> int:
        """
        Ingest all matching CSV files from a directory.
        
        Args:
            directory_path: Path to directory containing CSV files
            pattern: Glob pattern for matching files
        
        Returns:
            Total number of records inserted
        """
        total_inserted = 0
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                try:
                    count = self.ingest_file(file_path)
                    total_inserted += count
                except Exception as e:
                    print(f"Failed to process {file_path.name}: {e}")
                    continue
        
        print(f"Total records inserted: {total_inserted}")
        return total_inserted


def main():
    """Example usage of the ETL script"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.services.absorbance_etl <file_or_directory_path>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    etl = AbsorbanceETL()
    
    if input_path.is_file():
        etl.ingest_file(input_path)
    elif input_path.is_dir():
        etl.ingest_directory(input_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()

