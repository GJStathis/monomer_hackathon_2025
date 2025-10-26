#!/usr/bin/env python
"""
Script to ingest experiment data from CSV files.

Usage:
    python scripts/ingest_experiment_data.py <file_or_directory>
    
Examples:
    # Ingest a single experiment file
    python scripts/ingest_experiment_data.py "data/Costs analysis of chemicals  - exp 1.csv"
    
    # Ingest all experiment files in a directory
    python scripts/ingest_experiment_data.py data/
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.experiment_etl import ExperimentETL


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    # Initialize ETL
    etl = ExperimentETL(database_url="sqlite:///./database.db")
    
    print(f"Processing: {input_path}")
    print("-" * 60)
    
    try:
        if input_path.is_file():
            experiment_id = etl.ingest_file(input_path)
            print(f"\n✓ Successfully created experiment {experiment_id}")
        elif input_path.is_dir():
            experiment_ids = etl.ingest_directory(input_path, pattern="*exp*.csv")
            print(f"\n✓ Successfully created {len(experiment_ids)} experiments")
        else:
            print(f"Error: {input_path} is not a valid file or directory")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

