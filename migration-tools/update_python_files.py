#!/usr/bin/env python3
"""
Update Python Files for English Column Names
===========================================

This script updates all Python files to use the new English column names
after the database migration has been completed.

Usage: python update_python_files.py [--dry-run]
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_python_files(dry_run=False):
    """Update Python files to use new English column names"""
    logger.info("🔄 Updating Python files for new column names...")
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    # Files to update and their replacements
    files_to_update = {
        'database.py': [
            ('fecha = Column(Date', 'date = Column(Date'),
            ('valor = Column(Float', 'value = Column(Float'),
            ('año = Column(Integer', 'year = Column(Integer'),
            ('mes = Column(Integer', 'month = Column(Integer'),
        ],
        'services.py': [
            ('UIRecord.fecha', 'UIRecord.date'),
            ('URRecord.año', 'URRecord.year'),
            ('URRecord.mes', 'URRecord.month'),
            ('record.fecha', 'record.date'),
            ('record.valor', 'record.value'),
            ('record.año', 'record.year'),
            ('record.mes', 'record.month'),
            ('existing.valor', 'existing.value'),
        ],
        'excel_processor.py': [
            ('UIRecord.fecha', 'UIRecord.date'),
            ('URRecord.año', 'URRecord.year'),
            ('URRecord.mes', 'URRecord.month'),
            ('existing.valor', 'existing.value'),
            ('record.fecha', 'record.date'),
            ('record.valor', 'record.value'),
            ('record.año', 'record.year'),
            ('record.mes', 'record.month'),
            ('UIRecord(fecha=fecha, valor=valor)', 'UIRecord(date=fecha, value=valor)'),
            ('URRecord(año=year, mes=month, valor=value)', 'URRecord(year=year, month=month, value=value)'),
        ]
    }
    
    # Update constants.py
    constants_updates = [
        ('COLUMN_UI_DATE = "fecha"', 'COLUMN_UI_DATE = "date"'),
        ('COLUMN_UI_VALUE = "valor"', 'COLUMN_UI_VALUE = "value"'),
        ('COLUMN_UR_YEAR = "año"', 'COLUMN_UR_YEAR = "year"'),
        ('COLUMN_UR_MONTH = "mes"', 'COLUMN_UR_MONTH = "month"'),
        ('COLUMN_UR_VALUE = "valor"', 'COLUMN_UR_VALUE = "value"'),
        ('# Column names (keeping Spanish for database compatibility)', '# Column names (English for international standards)'),
    ]
    
    files_to_update['constants.py'] = constants_updates
    
    updated_files = []
    changes_made = {}
    
    for filename, replacements in files_to_update.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                file_changes = 0
                
                for old_text, new_text in replacements:
                    if old_text in content:
                        content = content.replace(old_text, new_text)
                        file_changes += content.count(new_text) - original_content.count(new_text)
                
                if content != original_content:
                    if not dry_run:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)
                    updated_files.append(filename)
                    changes_made[filename] = len([r for r in replacements if r[0] in original_content])
                    logger.info(f"✅ {'Would update' if dry_run else 'Updated'} {filename} ({changes_made[filename]} replacements)")
                else:
                    logger.info(f"ℹ️ No changes needed in {filename}")
                    
            except Exception as e:
                logger.error(f"❌ Error updating {filename}: {e}")
                return False
        else:
            logger.warning(f"⚠️ File {filename} not found")
    
    if dry_run:
        logger.info(f"🔍 DRY RUN: Would update {len(updated_files)} Python files")
        for filename, count in changes_made.items():
            logger.info(f"  - {filename}: {count} replacements")
    else:
        logger.info(f"🔄 Updated {len(updated_files)} Python files")
    
    return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update Python files for English column names')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    success = update_python_files(dry_run=args.dry_run)
    
    if success:
        if args.dry_run:
            logger.info("🔍 DRY RUN completed - no changes made")
        else:
            logger.info("🎉 Python files updated successfully!")
            logger.info("📋 Next steps:")
            logger.info("  1. Run tests to validate everything works")
            logger.info("  2. Check for any remaining manual updates needed")
            logger.info("  3. Update frontend if needed")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 