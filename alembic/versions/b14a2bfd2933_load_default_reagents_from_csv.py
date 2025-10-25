"""Load default reagents from CSV

Revision ID: b14a2bfd2933
Revises: 549dc6afa744
Create Date: 2025-10-25 15:12:54.039243

"""
from typing import Sequence, Union
import csv
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, String, Float, Integer


# revision identifiers, used by Alembic.
revision: str = 'b14a2bfd2933'
down_revision: Union[str, Sequence[str], None] = '549dc6afa744'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Load default reagents from CSV file."""
    # Define the reagent table structure for data insertion
    reagent_table = table('reagent',
        column('name', String),
        column('concentration', Float),
        column('unit', String)
    )
    
    # Get the CSV file path (relative to project root)
    csv_path = Path(__file__).parent.parent.parent / 'data' / 'default_reagnets.csv'
    
    # Read and insert data from CSV
    reagents_to_insert = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Handle NULL concentration values - set to 0.0 for liquids
            concentration = row['concentration'].strip()
            if concentration == 'NULL':
                concentration = 0.0
            else:
                concentration = float(concentration)
            
            reagents_to_insert.append({
                'name': row['name'].strip(),
                'concentration': concentration,
                'unit': row['unit'].strip()
            })
    
    # Bulk insert the data
    op.bulk_insert(reagent_table, reagents_to_insert)


def downgrade() -> None:
    """Remove the default reagents."""
    # Get the names from the CSV to delete them
    csv_path = Path(__file__).parent.parent.parent / 'local' / 'default_reagnets.csv'
    
    reagent_names = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        reagent_names = [row['name'].strip() for row in reader]
    
    # Delete the reagents by name
    connection = op.get_bind()
    for name in reagent_names:
        connection.execute(
            sa.text("DELETE FROM reagent WHERE name = :name"),
            {"name": name}
        )

