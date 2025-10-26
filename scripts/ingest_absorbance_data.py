#!/usr/bin/env python
"""
Script to ingest absorbance plate data from CSV files.

Usage:
    python scripts/ingest_absorbance_data.py <file_or_directory>
    
Examples:
    # Ingest a single file
    python scripts/ingest_absorbance_data.py data/plate_1_abs.csv
    
    # Ingest all absorbance files in a directory
    python scripts/ingest_absorbance_data.py data/
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.absorbance_etl import AbsorbanceETL


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    # Initialize ETL
    etl = AbsorbanceETL(database_url="sqlite:///./database.db")
    
    print(f"Processing: {input_path}")
    print("-" * 60)
    
    try:
        if input_path.is_file():
            count = etl.ingest_file(input_path)
            print(f"\n✓ Successfully ingested {count} records")
        elif input_path.is_dir():
            count = etl.ingest_directory(input_path, pattern="plate_*_abs.csv")
            print(f"\n✓ Successfully ingested {count} total records")
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

