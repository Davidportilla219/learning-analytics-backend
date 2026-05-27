"""
Migration to rename metadata field to event_metadata in events table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_rename_metadata_field'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Rename metadata column to event_metadata."""
    # First add the new column
    op.add_column('events',
        sa.Column('event_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    
    # Copy data from old column to new column
    op.execute("UPDATE events SET event_metadata = metadata WHERE metadata IS NOT NULL")
    
    # Drop the old column
    op.drop_column('events', 'metadata')
    
    # Add a comment for documentation
    op.create_comment(
        table='events',
        column='event_metadata',
        text="Additional metadata for the event"
    )


def downgrade():
    """Revert the migration by adding metadata column back."""
    # Add the old column back
    op.add_column('events',
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    
    # Copy data from new column to old column
    op.execute("UPDATE events SET metadata = event_metadata WHERE event_metadata IS NOT NULL")
    
    # Drop the new column
    op.drop_column('events', 'event_metadata')