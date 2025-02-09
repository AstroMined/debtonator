"""Excel data extraction utility for migrating historical data."""

import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

class ExcelExtractor:
    def __init__(self, excel_path: str):
        """Initialize the Excel extractor with the path to the Excel file.
        
        Args:
            excel_path: Path to the Excel file containing historical data
        """
        self.excel_path = excel_path
        
    def extract_bills(self) -> List[Dict]:
        """Extract bills data from the Excel sheet.
        
        Returns:
            List of dictionaries containing bill data
        """
        df = pd.read_excel(self.excel_path, sheet_name='Bills')
        
        bills = []
        for _, row in df.iterrows():
            bill = {
                'month': str(row['Month']),
                'day_of_month': int(row['Day of Month']),
                'due_date': row['Due Date'],
                'paid_date': row['Paid Date'] if pd.notna(row['Paid Date']) else None,
                'bill_name': str(row['Bill Name']),
                'amount': Decimal(str(row['Amount'])),
                'up_to_date': bool(row['Up To Date?']),
                'account': str(row['Account']),
                'auto_pay': bool(row['Auto Pay?']),
                'paid': bool(row['Paid?']),
                'amex_amount': Decimal(str(row['AMEX'])) if pd.notna(row['AMEX']) else None,
                'unlimited_amount': Decimal(str(row['Unlimited'])) if pd.notna(row['Unlimited']) else None,
                'ufcu_amount': Decimal(str(row['UFCU'])) if pd.notna(row['UFCU']) else None,
                'created_at': datetime.now().date(),
                'updated_at': datetime.now().date()
            }
            bills.append(bill)
            
        return bills
    
    def extract_income(self) -> List[Dict]:
        """Extract income data from the Excel sheet.
        
        Returns:
            List of dictionaries containing income data
        """
        df = pd.read_excel(self.excel_path, sheet_name='Income')
        
        income_entries = []
        for _, row in df.iterrows():
            income = {
                'date': row['Date'],
                'source': str(row['Income Source']),
                'amount': Decimal(str(row['Amount'])),
                'deposited': bool(row['Deposited?']),
                'undeposited_amount': Decimal(str(row['Income'])) if pd.notna(row['Income']) else Decimal('0'),
                'created_at': datetime.now().date(),
                'updated_at': datetime.now().date()
            }
            income_entries.append(income)
            
        return income_entries
    
    def extract_cashflow(self) -> List[Dict]:
        """Extract cashflow data from the Excel sheet.
        
        Returns:
            List of dictionaries containing cashflow data
        """
        df = pd.read_excel(self.excel_path, sheet_name='Cashflow')
        
        forecasts = []
        for _, row in df.iterrows():
            forecast = {
                'forecast_date': row['Date'],
                'total_bills': Decimal(str(row['Total Bills'])),
                'total_income': Decimal(str(row['Total Income'])),
                'balance': Decimal(str(row['Balance'])),
                'forecast': Decimal(str(row['Forecast'])),
                'min_14_day': Decimal(str(row['14 Day Min'])),
                'min_30_day': Decimal(str(row['30 Day Min'])),
                'min_60_day': Decimal(str(row['60 Day Min'])),
                'min_90_day': Decimal(str(row['90 Day Min'])),
                'daily_deficit': Decimal(str(row['Daily Deficit'])),
                'yearly_deficit': Decimal(str(row['Yearly Deficit'])),
                'required_income': Decimal(str(row['Required Income'])),
                'hourly_rate_40': Decimal(str(row['40 Hour Rate'])),
                'hourly_rate_30': Decimal(str(row['30 Hour Rate'])),
                'hourly_rate_20': Decimal(str(row['20 Hour Rate'])),
                'created_at': datetime.now().date(),
                'updated_at': datetime.now().date()
            }
            forecasts.append(forecast)
            
        return forecasts

    def validate_data(self, data: List[Dict], data_type: str) -> List[str]:
        """Validate extracted data for common issues.
        
        Args:
            data: List of extracted data dictionaries
            data_type: Type of data being validated ('bills', 'income', or 'cashflow')
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        for idx, item in enumerate(data):
            # Check for required fields based on data type
            if data_type == 'bills':
                required_fields = ['month', 'day_of_month', 'bill_name', 'amount', 'account']
            elif data_type == 'income':
                required_fields = ['date', 'source', 'amount']
            else:  # cashflow
                required_fields = ['forecast_date', 'total_bills', 'total_income', 'balance']
                
            for field in required_fields:
                if field not in item or item[field] is None:
                    errors.append(f"Missing required field '{field}' in {data_type} record {idx + 1}")
                    
            # Validate numeric fields
            numeric_fields = {
                'bills': ['amount', 'amex_amount', 'unlimited_amount', 'ufcu_amount'],
                'income': ['amount', 'undeposited_amount'],
                'cashflow': ['total_bills', 'total_income', 'balance', 'forecast', 
                           'min_14_day', 'min_30_day', 'min_60_day', 'min_90_day',
                           'daily_deficit', 'yearly_deficit', 'required_income',
                           'hourly_rate_40', 'hourly_rate_30', 'hourly_rate_20']
            }
            
            for field in numeric_fields.get(data_type, []):
                if field in item and item[field] is not None:
                    try:
                        if not isinstance(item[field], Decimal):
                            Decimal(str(item[field]))
                    except:
                        errors.append(f"Invalid numeric value for '{field}' in {data_type} record {idx + 1}")
                        
        return errors
