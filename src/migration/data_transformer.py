"""Transform extracted Excel data into SQLAlchemy models."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from src.models.bills import Bill
from src.models.cashflow import CashflowForecast
from src.models.income import Income


class DataTransformer:
    @staticmethod
    def transform_bills(bills_data: List[Dict[str, Any]]) -> List[Bill]:
        """Transform bills data into Bill models.

        Args:
            bills_data: List of dictionaries containing bill data

        Returns:
            List of Bill model instances
        """
        transformed_bills = []

        for bill_data in bills_data:
            bill = Bill(
                month=bill_data["month"],
                day_of_month=bill_data["day_of_month"],
                due_date=bill_data["due_date"],
                paid_date=bill_data["paid_date"],
                bill_name=bill_data["bill_name"],
                amount=bill_data["amount"],
                up_to_date=bill_data["up_to_date"],
                account=bill_data["account"],
                auto_pay=bill_data["auto_pay"],
                paid=bill_data["paid"],
                amex_amount=bill_data["amex_amount"],
                unlimited_amount=bill_data["unlimited_amount"],
                ufcu_amount=bill_data["ufcu_amount"],
                created_at=datetime.now().date(),
                updated_at=datetime.now().date(),
            )
            transformed_bills.append(bill)

        return transformed_bills

    @staticmethod
    def transform_income(income_data: List[Dict[str, Any]]) -> List[Income]:
        """Transform income data into Income models.

        Args:
            income_data: List of dictionaries containing income data

        Returns:
            List of Income model instances
        """
        transformed_income = []

        for income_entry in income_data:
            income = Income(
                date=income_entry["date"],
                source=income_entry["source"],
                amount=income_entry["amount"],
                deposited=income_entry["deposited"],
                undeposited_amount=income_entry["undeposited_amount"],
                created_at=datetime.now().date(),
                updated_at=datetime.now().date(),
            )
            transformed_income.append(income)

        return transformed_income

    @staticmethod
    def transform_cashflow(
        cashflow_data: List[Dict[str, Any]],
    ) -> List[CashflowForecast]:
        """Transform cashflow data into CashflowForecast models.

        Args:
            cashflow_data: List of dictionaries containing cashflow data

        Returns:
            List of CashflowForecast model instances
        """
        transformed_forecasts = []

        for forecast_data in cashflow_data:
            forecast = CashflowForecast(
                forecast_date=forecast_data["forecast_date"],
                total_bills=forecast_data["total_bills"],
                total_income=forecast_data["total_income"],
                balance=forecast_data["balance"],
                forecast=forecast_data["forecast"],
                min_14_day=forecast_data["min_14_day"],
                min_30_day=forecast_data["min_30_day"],
                min_60_day=forecast_data["min_60_day"],
                min_90_day=forecast_data["min_90_day"],
                daily_deficit=forecast_data["daily_deficit"],
                yearly_deficit=forecast_data["yearly_deficit"],
                required_income=forecast_data["required_income"],
                hourly_rate_40=forecast_data["hourly_rate_40"],
                hourly_rate_30=forecast_data["hourly_rate_30"],
                hourly_rate_20=forecast_data["hourly_rate_20"],
                created_at=datetime.now().date(),
                updated_at=datetime.now().date(),
            )
            transformed_forecasts.append(forecast)

        return transformed_forecasts
