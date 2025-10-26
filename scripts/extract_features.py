#!/usr/bin/env python
"""
Script to extract features from experiment and plate data.

Usage:
    python scripts/extract_features.py <experiment_id> <plate_id> [output_file]
    
Examples:
    # Extract features and display
    python scripts/extract_features.py 1 1
    
    # Extract features and save to CSV
    python scripts/extract_features.py 1 1 features_output.csv
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.feature_extractor import FeatureExtractor


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    experiment_id = int(sys.argv[1])
    plate_id = int(sys.argv[2])
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Initialize feature extractor
    extractor = FeatureExtractor(database_url="sqlite:///./database.db")
    
    print(f"Extracting features for Experiment {experiment_id} and Plate {plate_id}")
    print("=" * 60)
    
    try:
        # Get features dataframe
        df = extractor.get_features_dataframe(experiment_id, plate_id)
        
        # Display summary
        print(f"\n✓ Features DataFrame Generated")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Show feature columns
        feature_cols = [col for col in df.columns if col.startswith('feature_')]
        print(f"\n  Feature Columns ({len(feature_cols)}):")
        for col in feature_cols:
            print(f"    - {col}")
        
        # Display first few rows
        print(f"\n  Preview (first 5 rows):")
        print(df.head(5).to_string())
        
        # Display feature statistics
        print(f"\n  Feature Statistics:")
        feature_stats = df[[f'feature_{i}' for i in range(1, 17)]].describe()
        print(feature_stats.to_string())
        
        # Save to CSV if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"\n✓ Saved features to: {output_file}")
        else:
            # Default output file
            default_file = f"features_exp{experiment_id}_plate{plate_id}.csv"
            df.to_csv(default_file, index=False)
            print(f"\n✓ Saved features to: {default_file}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

