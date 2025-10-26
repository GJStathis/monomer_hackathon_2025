"""Description

Revision ID: 15a7037b391d
Revises: 8fe0ad5d725d
Create Date: 2025-10-26 10:23:43.990510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15a7037b391d'
down_revision: Union[str, Sequence[str], None] = '8fe0ad5d725d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: change concentration column from Float to String."""
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    # Create temporary table with new schema
    op.execute("""
        CREATE TABLE protocol_new (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            protocol_id INTEGER NOT NULL,
            reagent_name VARCHAR NOT NULL,
            concentration VARCHAR,
            unit VARCHAR NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(protocol_id) REFERENCES protocol_tracker (id)
        )
    """)
    
    # Copy data from old table to new table, converting concentration to string
    op.execute("""
        INSERT INTO protocol_new (id, protocol_id, reagent_name, concentration, unit, created_at)
        SELECT id, protocol_id, reagent_name, 
               CASE WHEN concentration IS NOT NULL THEN CAST(concentration AS TEXT) ELSE NULL END,
               unit, created_at
        FROM protocol
    """)
    
    # Drop old table
    op.drop_table('protocol')
    
    # Rename new table
    op.execute("ALTER TABLE protocol_new RENAME TO protocol")


def downgrade() -> None:
    """Downgrade schema: change concentration column from String to Float."""
    # Create temporary table with Float type
    op.execute("""
        CREATE TABLE protocol_new (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            protocol_id INTEGER NOT NULL,
            reagent_name VARCHAR NOT NULL,
            concentration FLOAT,
            unit VARCHAR NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(protocol_id) REFERENCES protocol_tracker (id)
        )
    """)
    
    # Copy data back, trying to convert string to float
    op.execute("""
        INSERT INTO protocol_new (id, protocol_id, reagent_name, concentration, unit, created_at)
        SELECT id, protocol_id, reagent_name,
               CASE WHEN concentration IS NOT NULL AND concentration != '' 
                    THEN CAST(concentration AS REAL) 
                    ELSE NULL END,
               unit, created_at
        FROM protocol
    """)
    
    # Drop old table
    op.drop_table('protocol')
    
    # Rename new table
    op.execute("ALTER TABLE protocol_new RENAME TO protocol")
