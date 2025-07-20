#!/usr/bin/env python3
"""
Database Migration Script: Spanish to English Column Names
=========================================================

This script migrates the database from Spanish column names to English:
- fecha -> date
- valor -> value  
- año -> year
- mes -> month

Usage: python migration_script.py [--dry-run] [--backup-only]
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    def __init__(self, db_path="ui_data.db"):
        self.db_path = db_path
        self.backup_path = f"ui_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
    def create_backup(self):
        """Create a backup of the current database"""
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, self.backup_path)
                logger.info(f"✅ Backup created: {self.backup_path}")
                return True
            else:
                logger.warning(f"⚠️ Database file {self.db_path} not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return False
    
    def validate_current_schema(self):
        """Validate current database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check UI table
            cursor.execute("PRAGMA table_info(ui_records)")
            ui_columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            # Check UR table  
            cursor.execute("PRAGMA table_info(ur_records)")
            ur_columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            conn.close()
            
            # Validate expected Spanish columns exist
            expected_ui = {'id', 'fecha', 'valor', 'created_at', 'updated_at'}
            expected_ur = {'id', 'año', 'mes', 'valor', 'created_at', 'updated_at'}
            
            if not expected_ui.issubset(set(ui_columns.keys())):
                logger.error(f"❌ UI table missing expected columns. Found: {list(ui_columns.keys())}")
                return False
                
            if not expected_ur.issubset(set(ur_columns.keys())):
                logger.error(f"❌ UR table missing expected columns. Found: {list(ur_columns.keys())}")
                return False
                
            logger.info("✅ Current schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating schema: {e}")
            return False
    
    def get_record_counts(self):
        """Get current record counts for validation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM ui_records")
            ui_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ur_records")  
            ur_count = cursor.fetchone()[0]
            
            conn.close()
            
            logger.info(f"📊 Current records - UI: {ui_count}, UR: {ur_count}")
            return ui_count, ur_count
            
        except Exception as e:
            logger.error(f"❌ Error getting record counts: {e}")
            return 0, 0
    
    def create_new_tables(self):
        """Create new tables with English column names"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Rename current tables to _old
            cursor.execute("ALTER TABLE ui_records RENAME TO ui_records_old")
            cursor.execute("ALTER TABLE ur_records RENAME TO ur_records_old")
            
            # Create new UI table with English columns
            cursor.execute("""
                CREATE TABLE ui_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    value REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create new UR table with English columns
            cursor.execute("""
                CREATE TABLE ur_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    value REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, month)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_ui_date ON ui_records(date)")
            cursor.execute("CREATE INDEX idx_ur_year_month ON ur_records(year, month)")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ New tables created with English column names")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating new tables: {e}")
            return False
    
    def migrate_data(self):
        """Migrate data from old tables to new tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Migrate UI data
            cursor.execute("""
                INSERT INTO ui_records (date, value, created_at, updated_at)
                SELECT fecha, valor, created_at, updated_at 
                FROM ui_records_old
            """)
            
            ui_migrated = cursor.rowcount
            
            # Migrate UR data
            cursor.execute("""
                INSERT INTO ur_records (year, month, value, created_at, updated_at)
                SELECT año, mes, valor, created_at, updated_at
                FROM ur_records_old
            """)
            
            ur_migrated = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Data migrated - UI: {ui_migrated} records, UR: {ur_migrated} records")
            return ui_migrated, ur_migrated
            
        except Exception as e:
            logger.error(f"❌ Error migrating data: {e}")
            return 0, 0
    
    def validate_migration(self, original_ui_count, original_ur_count):
        """Validate the migration was successful"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check new record counts
            cursor.execute("SELECT COUNT(*) FROM ui_records")
            new_ui_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ur_records")
            new_ur_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Validate counts match
            if new_ui_count != original_ui_count:
                logger.error(f"❌ UI record count mismatch: {original_ui_count} -> {new_ui_count}")
                return False
                
            if new_ur_count != original_ur_count:
                logger.error(f"❌ UR record count mismatch: {original_ur_count} -> {new_ur_count}")
                return False
            
            logger.info(f"✅ Migration validation passed")
            logger.info(f"📊 Final counts - UI: {new_ui_count}, UR: {new_ur_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating migration: {e}")
            return False
    
    def cleanup_old_tables(self):
        """Remove old tables after successful migration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS ui_records_old")
            cursor.execute("DROP TABLE IF EXISTS ur_records_old")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Old tables cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old tables: {e}")
            return False
    
    def run_migration(self, dry_run=False):
        """Run the complete migration process"""
        logger.info("🚀 Starting database migration: Spanish -> English column names")
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
        
        # Step 1: Create backup
        if not self.create_backup():
            logger.error("❌ Migration aborted - backup failed")
            return False
        
        # Step 2: Validate current schema
        if not self.validate_current_schema():
            logger.error("❌ Migration aborted - schema validation failed")
            return False
        
        # Step 3: Get current record counts
        original_ui_count, original_ur_count = self.get_record_counts()
        
        if dry_run:
            logger.info(f"🔍 DRY RUN: Would migrate UI records: {original_ui_count}, UR records: {original_ur_count}")
            return True
        
        # Step 4: Create new tables
        if not self.create_new_tables():
            logger.error("❌ Migration aborted - table creation failed")
            return False
        
        # Step 5: Migrate data
        migrated_ui, migrated_ur = self.migrate_data()
        if migrated_ui == 0 and migrated_ur == 0 and (original_ui_count > 0 or original_ur_count > 0):
            logger.error("❌ Migration aborted - data migration failed")
            return False
        
        # Step 6: Validate migration
        if not self.validate_migration(original_ui_count, original_ur_count):
            logger.error("❌ Migration aborted - validation failed")
            return False
        
        # Step 7: Cleanup old tables
        if not self.cleanup_old_tables():
            logger.warning("⚠️ Migration completed but cleanup failed")
        
        logger.info("🎉 Database migration completed successfully!")
        logger.info(f"💾 Backup available at: {self.backup_path}")
        
        return True


def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database from Spanish to English column names')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--backup-only', action='store_true', help='Only create backup, do not migrate')
    parser.add_argument('--db-path', default='ui_data.db', help='Path to database file')
    
    args = parser.parse_args()
    
    migration = DatabaseMigration(args.db_path)
    
    if args.backup_only:
        logger.info("📦 Creating backup only...")
        success = migration.create_backup()
        sys.exit(0 if success else 1)
    
    # Run database migration
    success = migration.run_migration(dry_run=args.dry_run)
    
    if success:
        if args.dry_run:
            logger.info("🔍 DRY RUN completed - no changes made")
        else:
            logger.info("🎉 Migration completed successfully!")
            logger.info("📋 Next steps:")
            logger.info("  1. Update Python files to use new column names")
            logger.info("  2. Run tests to validate everything works")
            logger.info("  3. Update frontend if needed")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 