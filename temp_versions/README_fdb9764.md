# Debtonator

A modern bill and cashflow management system that helps track bills, income, and maintain sufficient account balances for timely bill payments.

## Features

### Navigation & Interface
- Intuitive breadcrumb navigation for context
- Active route highlighting for better UX
- Collapsible account summary in sidebar
  - Real-time total balance display
  - Available credit tracking
  - Individual account balances
  - Color-coded status indicators
- Mobile-optimized navigation drawer
- Sticky positioning for better usability
- Version information display

### Account Management
- Dynamic account creation and configuration
- Support for multiple account types (credit, checking, savings)
- Enhanced balance tracking and visualization
  - Real-time balance history (last 30 entries)
  - Visual balance change indicators with up/down arrows
  - Color-coded balance status
  - Expandable account details
  - Credit account-specific information
- Statement balance history with visual indicators
- Mobile-optimized account grid view
- Comprehensive account overview with error handling
- Intuitive account management interface
- Seamless integration with bills and income features

### Bill Management
- Comprehensive bill tracking with enhanced visualization
- Intuitive split payment support with detailed tooltips
- Auto-pay status tracking with visual indicators
- Payment status management with bulk actions
- Due date tracking with overdue detection and visual feedback
- Mobile-optimized grid view with smart column management
- Advanced filtering and sorting capabilities
- Performance-optimized for large datasets
- Real-time calculations with optimistic updates
- Automatic state rollback on failures
- Efficient state updates with normalized structure
- Comprehensive pending updates tracking

### Financial Analysis
- Income tracking and deposit status
- Interactive cashflow visualization
  - 90-day rolling forecast with date range selection
  - Account balance trends with toggle functionality
  - Required funds comparison with period selection
  - Cross-account balance comparison
  - Real-time data updates
- Comprehensive financial metrics
  - Required funds calculation for multiple periods
  - Cross-account balance tracking
  - Deficit/surplus visualization

## Tech Stack

### Backend
- Python with FastAPI
- SQLite for development (MySQL/MariaDB for production)
- SQLAlchemy ORM
- Pydantic for data validation
- Alembic for database migrations

### Frontend
- React with TypeScript
- Redux Toolkit for state management
  - Type-safe state and actions
  - Efficient selectors and memoization
  - Real-time state synchronization
  - Normalized state structure
  - Optimistic updates with rollback
  - Pending updates tracking
  - Automatic recalculations
- Material-UI components
- Vite build system
- Jest and React Testing Library
- Formik and Yup for form handling

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
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── utils/          # Utilities
└── tests/              # Test suites
```

## State Management

The application uses Redux Toolkit with a focus on performance and reliability:

### Normalized State Structure
- Efficient lookups with Record<id, item>
- Reduced data duplication
- Optimized updates and selections

### Real-time Calculations
- Memoized selectors for performance
- Automatic recalculation on state changes
- Efficient filtering and aggregation

### Optimistic Updates
- Immediate UI feedback
- Automatic rollback on failures
- Pending updates tracking
- Original state preservation

### Type Safety
- Full TypeScript coverage
- Type-safe actions and state
- Comprehensive selector types

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
