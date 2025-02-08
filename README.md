# Debtonator

A modern bill and cashflow management system that helps track bills, income, and maintain sufficient account balances for timely bill payments.

## Features

- Track bills with payment status, due dates, and account allocation
- Record income sources and deposit status
- Monitor account balances and available credit
- Generate 90-day rolling cashflow forecasts
- Calculate minimum required funds for different periods
- Track recurring bills and payment patterns

## Project Status

Currently in active development. Completed features:
- Database schema with models for bills, income, accounts, and transactions
- Migration system with Alembic
- Performance indexes and relationships
- Development environment setup
- Bills API endpoints with:
  - CRUD operations
  - Date range filtering
  - Payment status management
  - Account-specific amount tracking

Next up:
- Income API endpoints
- Cashflow API endpoints
- Data migration tools
- Frontend development
- Testing infrastructure

## Development Setup

### Prerequisites
- Python 3.10+
- SQLite (for development)

### Installation

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start development server:
```bash
python run.py
```

## API Documentation

The API documentation is available at `/docs` when running the development server.

### Bills API Endpoints

- `GET /api/v1/bills/` - List all bills with pagination
- `POST /api/v1/bills/` - Create a new bill
- `GET /api/v1/bills/{id}` - Get a specific bill
- `PUT /api/v1/bills/{id}` - Update a bill
- `DELETE /api/v1/bills/{id}` - Delete a bill
- `GET /api/v1/bills/unpaid/` - List unpaid bills
- `GET /api/v1/bills/by-date-range/` - Get bills within date range
- `PATCH /api/v1/bills/{id}/mark-paid` - Mark a bill as paid

## Project Structure

```
debtonator/
├── alembic/              # Database migrations
├── docs/                 # Project documentation
│   ├── adr/             # Architecture Decision Records
│   └── ...              # Other documentation
├── src/
│   ├── api/             # API endpoints
│   │   └── v1/          # API version 1
│   ├── database/        # Database configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
└── tests/               # Test suite
    ├── integration/     # Integration tests
    └── unit/           # Unit tests
```

## Documentation

- [Project Brief](docs/project_brief.md)
- [Technical Context](docs/tech_context.md)
- [System Patterns](docs/system_patterns.md)
- [Architecture Decisions](docs/adr/)

## Contributing

1. Check the [Active Context](docs/active_context.md) for current focus
2. Review [Progress](docs/progress.md) for status
3. Follow project patterns in [System Patterns](docs/system_patterns.md)

## License

[MIT License](LICENSE)
