# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup and documentation
- Database schema design and implementation
  - Core models (Bills, Income, Accounts)
  - Supporting models (Transactions, RecurringBills, CashflowForecasts)
  - Model relationships and foreign keys
  - Performance indexes
- Development environment configuration
  - Python virtual environment with UV
  - SQLite database setup
  - Configuration management (.env)
  - FastAPI project structure
- Database migration system
  - Alembic configuration
  - Initial schema migration
  - Migration for relationships and indexes
- Project documentation
  - Project brief and requirements
  - Technical context and patterns
  - Architecture decisions
  - Progress tracking

### Changed
- Converted from Excel-based system to database schema
- Updated bill tracking to use proper relationships
- Enhanced account management with transaction tracking

### Technical Details
- Added foreign key from bills to accounts
- Created indexes for efficient querying:
  - Bills: due_date, paid_date, account_id
  - Income: date, deposited status
  - Transactions: date, account_id
  - Accounts: name
  - Cashflow: date
- Implemented calculation methods in models
- Set up async database support
