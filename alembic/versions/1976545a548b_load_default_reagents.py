"""Load default reagents

Revision ID: 1976545a548b
Revises: 4642e69619c1
Create Date: 2025-10-25 16:08:00.000000

"""
from typing import Sequence, Union
import csv
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, String, Float


# revision identifiers, used by Alembic.
revision: str = '1976545a548b'
down_revision: Union[str, Sequence[str], None] = '4642e69619c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Load default reagents from CSV file."""
    reagent_table = table('reagent',
        column('name', String),
        column('concentration', Float),
        column('unit', String)
    )
    
    csv_path = Path(__file__).parent.parent.parent / 'data' / 'default_reagnets.csv'
    
    reagents_to_insert = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
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
    
    op.bulk_insert(reagent_table, reagents_to_insert)


def downgrade() -> None:
    """Remove the default reagents."""
    csv_path = Path(__file__).parent.parent.parent / 'data' / 'default_reagnets.csv'
    
    reagent_names = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        reagent_names = [row['name'].strip() for row in reader]
    
    connection = op.get_bind()
    for name in reagent_names:
        connection.execute(
            sa.text("DELETE FROM reagent WHERE name = :name"),
            {"name": name}
        )

