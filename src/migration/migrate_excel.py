#!/usr/bin/env python3
"""CLI script for migrating Excel data to the SQLite database."""

import asyncio
import argparse
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.migration.database_importer import DatabaseImporter
from src.utils.config import get_settings

async def migrate_data(excel_path: str) -> None:
    """Migrate data from Excel to SQLite database.
    
    Args:
        excel_path: Path to the Excel file containing historical data
    """
    if not Path(excel_path).exists():
        print(f"Error: Excel file not found at {excel_path}")
        sys.exit(1)
        
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        importer = DatabaseImporter(session, excel_path)
        
        print("\nStarting data migration...")
        
        # Import bills
        print("\nImporting bills...")
        bills_stats = await importer.import_bills()
        print(f"Bills imported: {bills_stats['success']}/{bills_stats['total']}")
        if bills_stats["errors"]:
            print("Bills import errors:")
            for error in bills_stats["errors"]:
                print(f"  - {error}")
                
        # Import income
        print("\nImporting income...")
        income_stats = await importer.import_income()
        print(f"Income entries imported: {income_stats['success']}/{income_stats['total']}")
        if income_stats["errors"]:
            print("Income import errors:")
            for error in income_stats["errors"]:
                print(f"  - {error}")
                
        # Import cashflow
        print("\nImporting cashflow...")
        cashflow_stats = await importer.import_cashflow()
        print(f"Cashflow entries imported: {cashflow_stats['success']}/{cashflow_stats['total']}")
        if cashflow_stats["errors"]:
            print("Cashflow import errors:")
            for error in cashflow_stats["errors"]:
                print(f"  - {error}")
                
        # Verify import
        print("\nVerifying import...")
        verification = await importer.verify_import()
        print("\nImport verification results:")
        print(f"  Bills: {verification['bills']['count']} records")
        print(f"  Income: {verification['income']['count']} records")
        print(f"  Cashflow: {verification['cashflow']['count']} records")
        
        if any(verification[key]["errors"] for key in verification):
            print("\nVerification errors:")
            for key in verification:
                for error in verification[key]["errors"]:
                    print(f"  - {error}")
                    
        print("\nMigration complete!")

def main():
    parser = argparse.ArgumentParser(description="Migrate Excel data to SQLite database")
    parser.add_argument(
        "excel_path",
        help="Path to the Excel file containing historical data"
    )
    
    args = parser.parse_args()
    asyncio.run(migrate_data(args.excel_path))

if __name__ == "__main__":
    main()
