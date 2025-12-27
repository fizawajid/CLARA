"""Migration script to add aspect_results column to analysis_results table."""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def migrate_database():
    """Add aspect_results column to existing database."""

    db_path = project_root / "nlp_feedback.db"

    if not db_path.exists():
        logger.info("Database does not exist yet. No migration needed.")
        return

    logger.info(f"Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(analysis_results)")
        columns = [row[1] for row in cursor.fetchall()]

        if "aspect_results" in columns:
            logger.info("Column 'aspect_results' already exists. No migration needed.")
            conn.close()
            return

        # Add the column
        logger.info("Adding 'aspect_results' column...")
        cursor.execute("""
            ALTER TABLE analysis_results
            ADD COLUMN aspect_results JSON
        """)

        conn.commit()
        logger.info("✓ Migration successful: aspect_results column added")

        conn.close()

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 60)
    print("Database Migration: Add aspect_results Column")
    print("=" * 60)

    migrate_database()

    print("\n✅ Migration complete!")
