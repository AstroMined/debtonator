# Project Brief: Debtonator - Bill & Cashflow Management System

## Overview
Convert an existing Excel-based bill and cashflow management system into a modern web application with future mobile capabilities. The system helps users track bills, income, and maintain sufficient account balances for timely bill payments.

## Core Requirements

### Account Management
- Dynamic account management:
  - Support for multiple account types (credit, checking, savings)
  - Track available balances
  - Monitor credit limits and available credit
  - Statement balance tracking
  - Account-specific transaction history

### Bill Management
- Track bills with key attributes:
  - Due date (Month/Day)
  - Payment status
  - Bill name
  - Amount
  - Primary account assignment
  - Split payment support across multiple accounts
  - Auto-pay status
  - Payment tracking (Paid/Unpaid)

### Bill Split Features
- Support for splitting bills across multiple accounts
- Split amount validation
- Split payment tracking
- Balance impact tracking per account
- Historical split payment records

### Income Tracking
- Record income sources with:
  - Date
  - Source name
  - Amount
  - Deposit status
  - Running total of undeposited income
  - Target account for deposits

### Cashflow Analysis
- 90-day rolling forecast of financial position
- Track available credit/balance across all accounts
- Calculate minimum required funds for different periods:
  - 14-day outlook
  - 30-day outlook
  - 60-day outlook
  - 90-day outlook
- Calculate required additional income:
  - Daily deficit
  - Yearly deficit
  - Extra income needed (with tax consideration)
  - Hourly rate needed at different work hours (40/30/20 per week)

## Technical Requirements

### Backend
- Python-based using FastAPI
- Pydantic for data validation
- SQLite for development
- MySQL/MariaDB for production
- Efficient database schema for account relationships
- Split payment validation and processing

### Frontend
- React-based web application with TypeScript
- Mobile-responsive design
- Real-time calculations
- Clear visualization of financial status
- Dynamic account management interface
- Split payment entry and tracking
- Material-UI components
- Form validation with Formik and Yup

### Future Extensions
- Native mobile applications (Android/iOS)
- Real-time synchronization between devices
- Banking API integration
- Notification system for:
  - Upcoming bills
  - Low balances
  - Credit limit warnings
  - Split payment reminders
- Account balance reconciliation
- Automated split suggestions

## Success Criteria
1. Maintain all current spreadsheet functionality
2. Improve ease of data entry and updates
3. Provide clearer visualization of financial status
4. Enable easier access through web interface
5. Maintain data accuracy and reliability
6. Support flexible account management
7. Enable efficient split payment handling
8. Provide accurate balance tracking across accounts

## Data Migration
1. Preserve historical data since 2017
2. Convert account-specific amounts to split payments
3. Maintain payment history and relationships
4. Ensure data integrity during migration
5. Validate calculations after migration

## User Experience Goals
1. Intuitive account management
2. Simple split payment entry
3. Clear financial status visualization
4. Easy bill management
5. Efficient data entry
6. Mobile-friendly interface
7. Real-time updates
8. Responsive design
