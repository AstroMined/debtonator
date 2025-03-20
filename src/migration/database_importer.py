"""Database importer for migrating Excel data into the SQLite database."""

import asyncio
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.migration.data_transformer import DataTransformer
from src.migration.excel_extractor import ExcelExtractor
from src.models.bills import Bill
from src.models.cashflow import CashflowForecast
from src.models.income import Income


class DatabaseImporter:
    def __init__(self, session: AsyncSession, excel_path: str):
        """Initialize the database importer.

        Args:
            session: SQLAlchemy async session
            excel_path: Path to the Excel file
        """
        self.session = session
        self.extractor = ExcelExtractor(excel_path)
        self.transformer = DataTransformer()

    async def import_bills(self) -> Dict[str, Any]:
        """Import bills data from Excel into the database.

        Returns:
            Dictionary containing import statistics
        """
        stats = {"total": 0, "success": 0, "errors": []}

        try:
            # Extract and validate
            bills_data = self.extractor.extract_bills()
            validation_errors = self.extractor.validate_data(bills_data, "bills")
            if validation_errors:
                stats["errors"].extend(validation_errors)
                return stats

            # Transform
            bills = self.transformer.transform_bills(bills_data)
            stats["total"] = len(bills)

            # Import in batches
            batch_size = 100
            for i in range(0, len(bills), batch_size):
                batch = bills[i : i + batch_size]
                try:
                    self.session.add_all(batch)
                    await self.session.commit()
                    stats["success"] += len(batch)
                except Exception as e:
                    await self.session.rollback()
                    stats["errors"].append(
                        f"Error importing bills batch {i//batch_size + 1}: {str(e)}"
                    )

        except Exception as e:
            stats["errors"].append(f"Error during bills import: {str(e)}")

        return stats

    async def import_income(self) -> Dict[str, Any]:
        """Import income data from Excel into the database.

        Returns:
            Dictionary containing import statistics
        """
        stats = {"total": 0, "success": 0, "errors": []}

        try:
            # Extract and validate
            income_data = self.extractor.extract_income()
            validation_errors = self.extractor.validate_data(income_data, "income")
            if validation_errors:
                stats["errors"].extend(validation_errors)
                return stats

            # Transform
            income_entries = self.transformer.transform_income(income_data)
            stats["total"] = len(income_entries)

            # Import in batches
            batch_size = 100
            for i in range(0, len(income_entries), batch_size):
                batch = income_entries[i : i + batch_size]
                try:
                    self.session.add_all(batch)
                    await self.session.commit()
                    stats["success"] += len(batch)
                except Exception as e:
                    await self.session.rollback()
                    stats["errors"].append(
                        f"Error importing income batch {i//batch_size + 1}: {str(e)}"
                    )

        except Exception as e:
            stats["errors"].append(f"Error during income import: {str(e)}")

        return stats

    async def import_cashflow(self) -> Dict[str, Any]:
        """Import cashflow data from Excel into the database.

        Returns:
            Dictionary containing import statistics
        """
        stats = {"total": 0, "success": 0, "errors": []}

        try:
            # Extract and validate
            cashflow_data = self.extractor.extract_cashflow()
            validation_errors = self.extractor.validate_data(cashflow_data, "cashflow")
            if validation_errors:
                stats["errors"].extend(validation_errors)
                return stats

            # Transform
            forecasts = self.transformer.transform_cashflow(cashflow_data)
            stats["total"] = len(forecasts)

            # Import in batches
            batch_size = 100
            for i in range(0, len(forecasts), batch_size):
                batch = forecasts[i : i + batch_size]
                try:
                    self.session.add_all(batch)
                    await self.session.commit()
                    stats["success"] += len(batch)
                except Exception as e:
                    await self.session.rollback()
                    stats["errors"].append(
                        f"Error importing cashflow batch {i//batch_size + 1}: {str(e)}"
                    )

        except Exception as e:
            stats["errors"].append(f"Error during cashflow import: {str(e)}")

        return stats

    async def verify_import(self) -> Dict[str, Any]:
        """Verify the imported data by checking record counts.

        Returns:
            Dictionary containing verification results
        """
        verification = {
            "bills": {"count": 0, "errors": []},
            "income": {"count": 0, "errors": []},
            "cashflow": {"count": 0, "errors": []},
        }

        try:
            # Check bills
            result = await self.session.execute(select(Bill))
            verification["bills"]["count"] = len(result.scalars().all())

            # Check income
            result = await self.session.execute(select(Income))
            verification["income"]["count"] = len(result.scalars().all())

            # Check cashflow
            result = await self.session.execute(select(CashflowForecast))
            verification["cashflow"]["count"] = len(result.scalars().all())

        except Exception as e:
            verification["errors"] = [f"Error during verification: {str(e)}"]

        return verification
