import pandas as pd
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repositories.experiment_repository import ExperimentRepository
from src.repositories.reagent_value_repository import ReagentValueRepository
from src.repositories.plate_repository import PlateRepository


class FeatureExtractor:
    """
    Service to extract features from experiment and plate data.
    
    Combines reagent values from experiments with plate measurements
    to create a feature matrix for analysis.
    """
    
    def __init__(self, database_url: str = "sqlite:///./database.db"):
        """Initialize feature extractor with database connection"""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_features_dataframe(self, experiment_id: int, plate_id: int) -> pd.DataFrame:
        """
        Generate a features dataframe combining experiment and plate data.
        
        The dataframe includes:
        - feature_1 through feature_15: Reagent values from the experiment
        - feature_16: cell_concentration / (dilution * row_index)
        - Additional columns: plate_id, well info, time, absorbance value
        
        Args:
            experiment_id: ID of the experiment
            plate_id: ID of the plate
        
        Returns:
            pandas DataFrame with features for each plate measurement
        """
        session = self.SessionLocal()
        
        try:
            # Initialize repositories
            experiment_repo = ExperimentRepository(session)
            reagent_value_repo = ReagentValueRepository(session)
            plate_repo = PlateRepository(session)
            
            # Get experiment data
            experiment = experiment_repo.get_by_id(experiment_id)
            if not experiment:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            # Get reagent values for the experiment
            reagent_values = reagent_value_repo.get_by_experiment_id(experiment_id)
            
            # Sort reagent values by reagent_id to ensure consistent ordering
            reagent_values_sorted = sorted(reagent_values, key=lambda rv: rv.reagent_id)
            
            # Get plate data
            plate_data = plate_repo.get_by_plate_id(plate_id)
            if not plate_data:
                raise ValueError(f"No data found for plate {plate_id}")
            
            # Create base dataframe from plate data
            plate_records = []
            for record in plate_data:
                plate_records.append({
                    'plate_id': record.plate_id,
                    'row_id': record.row_id,
                    'column_id': record.column_id,
                    'absorbance': record.value,
                    'seconds_time_sample': record.seconds_time_sample,
                    'created_at': record.created_at
                })
            
            df = pd.DataFrame(plate_records)
            
            # Add reagent features (feature_1 through feature_15)
            for idx, reagent_value in enumerate(reagent_values_sorted, start=1):
                if idx <= 15:  # Limit to 15 reagent features
                    df[f'feature_{idx}'] = reagent_value.value
            
            # Fill any missing features (if less than 15 reagents) with 0
            for idx in range(1, 16):
                if f'feature_{idx}' not in df.columns:
                    df[f'feature_{idx}'] = 0.0
            
            # Calculate feature_16: cell_concentration / (dilution * row_index)
            # Row index is 1-based (each row in the dataframe)
            df['row_index'] = range(1, len(df) + 1)
            df['feature_16'] = experiment.cell_concentration / (experiment.dilution * df['row_index'])
            
            # Reorder columns to have features first
            feature_cols = [f'feature_{i}' for i in range(1, 17)]
            other_cols = ['plate_id', 'row_id', 'column_id', 'seconds_time_sample', 'absorbance', 'created_at']
            
            # Only include columns that exist
            final_cols = feature_cols + [col for col in other_cols if col in df.columns]
            df = df[final_cols]
            
            return df
            
        finally:
            session.close()
    
    def get_features_summary(self, experiment_id: int, plate_id: int) -> dict:
        """
        Get a summary of the features extracted.
        
        Args:
            experiment_id: ID of the experiment
            plate_id: ID of the plate
        
        Returns:
            Dictionary with summary statistics
        """
        df = self.get_features_dataframe(experiment_id, plate_id)
        
        return {
            'num_records': len(df),
            'num_features': 16,
            'plate_id': plate_id,
            'experiment_id': experiment_id,
            'feature_columns': [col for col in df.columns if col.startswith('feature_')],
            'shape': df.shape,
            'feature_stats': df[[f'feature_{i}' for i in range(1, 17)]].describe().to_dict()
        }


def main():
    """Example usage of the feature extractor"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m src.services.feature_extractor <experiment_id> <plate_id>")
        sys.exit(1)
    
    experiment_id = int(sys.argv[1])
    plate_id = int(sys.argv[2])
    
    extractor = FeatureExtractor()
    
    print(f"Extracting features for experiment {experiment_id} and plate {plate_id}")
    print("-" * 60)
    
    # Get features dataframe
    df = extractor.get_features_dataframe(experiment_id, plate_id)
    
    print(f"\nFeatures DataFrame:")
    print(f"Shape: {df.shape}")
    print(f"\nFirst 10 rows:")
    print(df.head(10))
    
    print(f"\nFeature columns:")
    feature_cols = [col for col in df.columns if col.startswith('feature_')]
    print(feature_cols)
    
    print(f"\nSummary statistics:")
    summary = extractor.get_features_summary(experiment_id, plate_id)
    print(f"Number of records: {summary['num_records']}")
    print(f"Number of features: {summary['num_features']}")
    
    # Optionally save to CSV
    output_file = f"features_exp{experiment_id}_plate{plate_id}.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved features to: {output_file}")


if __name__ == "__main__":
    main()

