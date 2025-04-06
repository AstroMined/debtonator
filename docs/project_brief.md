# Project Brief: Debtonator - Financial Management Platform

## Overview

Debtonator is a comprehensive financial management platform designed to provide users with a "single pane of glass" view of their financial life. This system helps users track bills, income, and maintain sufficient account balances for timely bill payments, while serving as the foundation for a broader vision of financial empowerment.

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
- Flexible deficit tracking and planning:
  - Daily/weekly/monthly/yearly deficit or surplus tracking
  - Customizable additional income planning tools
  - "Side gig" impact calculator for various earning scenarios
  - Visualization of how additional income affects financial outlook

### Debt Management

- Track debt balances and payment progress
- Support for "snowball" and "avalanche" debt reduction strategies
- Visualization of debt payoff timeline
- Impact analysis of additional payments

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
- Community-based financial empowerment features

## Success Criteria

1. Provide a comprehensive view of a user's financial status
2. Deliver intuitive and efficient financial management tools
3. Enable accurate financial forecasting
4. Provide clear visualization of financial status
5. Support flexible account management
6. Enable efficient split payment handling
7. Provide accurate balance tracking across accounts
8. Help users develop pathways to debt reduction

## User Experience Goals

1. Intuitive account management
2. Simple split payment entry
3. Clear financial status visualization
4. Easy bill management
5. Efficient data entry
6. Mobile-friendly interface
7. Real-time updates
8. Responsive design
9. Empowering financial insights
10. Actionable debt reduction strategies
