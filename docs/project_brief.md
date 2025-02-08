# Project Brief: Debtonator - Bill & Cashflow Management System

## Overview
Convert an existing Excel-based bill and cashflow management system into a modern web application with future mobile capabilities. The system helps users track bills, income, and maintain sufficient account balances for timely bill payments.

## Core Requirements

### Bill Management
- Track bills with key attributes:
  - Due date (Month/Day)
  - Payment status
  - Bill name
  - Amount
  - Account (AMEX, UFCU, Unlimited)
  - Auto-pay status
  - Payment tracking (Paid/Unpaid)

### Income Tracking
- Record income sources with:
  - Date
  - Source name
  - Amount
  - Deposit status
  - Running total of undeposited income

### Cashflow Analysis
- 90-day rolling forecast of financial position
- Track available credit/balance across accounts
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

### Frontend
- React-based web application
- Mobile-responsive design
- Real-time calculations
- Clear visualization of financial status

### Future Extensions
- Native mobile applications (Android/iOS)
- Real-time synchronization between devices
- Banking API integration
- Notification system for upcoming bills/low balances

## Success Criteria
1. Maintain all current spreadsheet functionality
2. Improve ease of data entry and updates
3. Provide clearer visualization of financial status
4. Enable easier access through web interface
5. Maintain data accuracy and reliability
