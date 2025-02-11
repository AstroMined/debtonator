# Debtonator v1.2.0

A modern bill and cashflow management system that helps track bills, income, and maintain sufficient account balances for timely bill payments.

## Features

### Account Management
- Dynamic account creation and configuration
- Support for multiple account types (credit, checking, savings)
- Real-time balance and credit limit tracking
- Statement balance history with visual indicators
- Mobile-optimized account grid view
- Comprehensive account overview with error handling
- Intuitive account management interface
- Seamless integration with liabilities and income features

### Liability Management
- Comprehensive liability (bill) tracking with enhanced visualization
- Intuitive split payment support with detailed tooltips
- Auto-pay status tracking with visual indicators
- Payment status management with bulk actions
- Due date tracking with overdue detection and visual feedback
- Mobile-optimized grid view with smart column management
- Advanced filtering and sorting capabilities
- Performance-optimized for large datasets
- Support for recurring patterns and categorization
- Clear separation of liabilities and payments
- Flexible payment source tracking

### Financial Analysis
- Income tracking and deposit status
- Interactive cashflow visualization
  - 90-day rolling forecast with date range selection
  - Account balance trends with toggle functionality
  - Required funds comparison with period selection
  - Cross-account balance comparison
  - Real-time data updates (5-minute polling)
  - Interactive tooltips with detailed data points
  - Brush component for date range selection
  - Visual deficit/surplus indicators
- Comprehensive financial metrics
  - Required funds calculation for multiple periods
  - Cross-account balance tracking
  - Deficit/surplus visualization
  - Historical payment analysis
  - Payment source distribution metrics

### Data Management
- Bulk import functionality for liabilities and income
  - Support for CSV and JSON file formats
  - File upload interface with drag-and-drop support
  - Data validation and preview before import
  - Progress tracking and error reporting
  - Import status notifications
  - Documentation for import file formats
- Historical data entry support
- Data migration tools with rollback support

## Tech Stack

### Backend
- Python with FastAPI
- SQLite for development (MySQL/MariaDB for production)
- SQLAlchemy ORM with async support
- Pydantic for data validation
- Alembic for database migrations
- Comprehensive test suite with async support
- Advanced error handling and validation

### Frontend
- React with TypeScript
- Redux Toolkit for state management
  - Type-safe state and actions
  - Efficient selectors and memoization
  - Real-time state synchronization
  - Optimistic updates with rollback
  - Normalized state structure
  - Comprehensive pending updates tracking
- Material-UI components
- Vite build system
- Jest and React Testing Library
- Formik and Yup for form handling
- Recharts for data visualization

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- SQLite3

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/debtonator.git
cd debtonator
```

2. Set up Python environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Initialize database
```bash
alembic upgrade head
```

5. Install frontend dependencies
```bash
cd frontend
npm install
```

### Running the Application

1. Start the backend server
```bash
# From the root directory
python run.py
```

2. Start the frontend development server
```bash
# From the frontend directory
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs

## Project Structure

```
debtonator/
├── alembic/              # Database migrations
├── docs/                 # Project documentation
│   ├── adr/             # Architecture Decision Records
│   └── ...              # Other documentation
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Redux store and slices
│   │   │   └── slices/  # Feature-specific slices
│   │   └── types/       # TypeScript types
│   └── ...
├── src/                 # Backend application
│   ├── api/            # API endpoints
│   ├── models/         # Database models
│   │   ├── liabilities.py  # Bill tracking (liabilities)
│   │   ├── payments.py     # Payment and source tracking
│   │   └── ...            # Other models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── utils/          # Utilities
└── tests/              # Test suites (temporarily removed for restructuring)
```

## Core Architecture

### Double-Entry Payment Tracking
The system uses a modified double-entry accounting approach with three core entities:

1. **Liabilities (Bills)**
   - Represent what is owed
   - Track due dates and amounts
   - Support recurring patterns
   - Categorization support
   - Historical tracking
   - Support for complex payment scenarios

2. **Payments (Transactions)**
   - Record actual payments made
   - Link to bills (optional)
   - Support non-bill expenses
   - Track payment dates
   - Maintain payment history
   - Support for partial payments

3. **Payment Sources (Entries)**
   - Track which accounts funded payments
   - Support split payments
   - Maintain account balance accuracy
   - Handle complex payment distributions
   - Support for multiple funding sources
   - Track payment source history

This architecture provides:
- Clear separation of bills and payments
- Better support for complex payment scenarios
- Natural fit for non-bill expenses
- Improved historical tracking
- Better analytics capabilities
- More flexible payment handling
- Enhanced reporting capabilities
- Improved data consistency
- Better support for financial analysis

## Documentation

- [Project Brief](docs/project_brief.md)
- [Technical Context](docs/tech_context.md)
- [System Patterns](docs/system_patterns.md)
- [API Documentation](http://localhost:8000/api/v1/docs)

## Architecture Decisions

- [Database Schema Design](docs/adr/001-database-schema-design.md)
- [Historical Data Entry](docs/adr/002-historical-data-entry.md)
- [Dynamic Accounts and Bill Splits](docs/adr/003-dynamic-accounts-and-bill-splits.md)
- [Bills Table Dynamic Accounts](docs/adr/004-bills-table-dynamic-accounts.md)
- [Bills Table UI/UX Enhancements](docs/adr/005-bills-table-enhancements.md)
- [Redux Toolkit State Management](docs/adr/006-redux-toolkit-state-management.md)
- [Bulk Import Functionality](docs/adr/007-bulk-import-functionality.md)
- [Bill Splits Implementation](docs/adr/008-bill-splits-implementation.md)
- [Bills/Payments Separation](docs/adr/009-bills-payments-separation.md)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
