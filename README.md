# Debtonator

A modern bill and cashflow management system built with FastAPI and React.

## Overview

Debtonator helps users track bills, income, and maintain sufficient account balances for timely bill payments. It provides real-time financial forecasting and calculates required income based on upcoming expenses.

## Features

### Bill Management
- Track bills with due dates, amounts, and payment status
- Support for multiple payment accounts (AMEX, UFCU, Unlimited)
- Auto-pay status tracking
- Historical payment records
- Date range filtering

### Income Tracking
- Record and track income sources
- Deposit status management
- Undeposited income tracking
- Running total calculations
- Source categorization

### Cashflow Analysis
- 90-day rolling forecast
- Available credit/balance tracking
- Minimum required funds calculation:
  - 14-day outlook
  - 30-day outlook
  - 60-day outlook
  - 90-day outlook
- Required income projections:
  - Daily deficit
  - Yearly deficit
  - Extra income needed (with tax consideration)
  - Hourly rate calculations (40/30/20 hours per week)

## Technology Stack

### Backend
- FastAPI for high-performance API
- SQLite for development (MySQL/MariaDB for production)
- Pydantic for data validation
- SQLAlchemy for ORM
- Alembic for migrations

### Frontend
- React with TypeScript
- Vite for build tooling
- Jest and React Testing Library
- ESLint and Prettier for code quality
- Mobile-responsive design
- Real-time calculations

## API Documentation

### Bills API
- `GET /api/v1/bills/` - List bills with filtering
- `POST /api/v1/bills/` - Create new bill
- `GET /api/v1/bills/{id}` - Get bill details
- `PUT /api/v1/bills/{id}` - Update bill
- `DELETE /api/v1/bills/{id}` - Delete bill
- `PUT /api/v1/bills/{id}/pay` - Mark bill as paid

### Income API
- `GET /api/v1/income/` - List income records with filtering
- `POST /api/v1/income/` - Create new income record
- `GET /api/v1/income/{id}` - Get income details
- `PUT /api/v1/income/{id}` - Update income record
- `DELETE /api/v1/income/{id}` - Delete income record
- `GET /api/v1/income/undeposited/` - List undeposited income
- `PUT /api/v1/income/{id}/deposit` - Mark income as deposited
- `GET /api/v1/income/undeposited/total/` - Get total undeposited amount

### Cashflow API
- `GET /api/v1/cashflow/` - List cashflow forecasts
- `POST /api/v1/cashflow/forecast/90-day` - Calculate 90-day forecast
- `GET /api/v1/cashflow/{id}` - Get forecast details
- `GET /api/v1/cashflow/{id}/minimum-required` - Get minimum required funds
- `GET /api/v1/cashflow/{id}/deficit` - Get deficit calculations
- `GET /api/v1/cashflow/{id}/hourly-rates` - Get required hourly rates

## Setup

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/debtonator.git
cd debtonator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. (Optional) Migrate historical Excel data:
```bash
python src/migration/migrate_excel.py path/to/excel_file.xlsx
```

7. Start the development server:
```bash
uvicorn src.main:app --reload
```

8. Access the API documentation:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm run dev
```

5. Access the application:
- Development: http://localhost:3000

## Development Status

### Completed
- ✓ Backend API structure
- ✓ Database models and migrations
- ✓ Bills API endpoints
- ✓ Income API endpoints
- ✓ Cashflow API endpoints
- ✓ Core business logic
- ✓ API documentation
- ✓ Data migration tools
  - Excel data extraction
  - Data transformation
  - Database import with validation
  - Migration CLI tool
- ✓ Frontend development setup
  - React with TypeScript
  - Build system and testing
  - Code quality tools
  - Project structure

### In Progress
- Frontend feature components development
  - Bills management interface
  - Income tracking interface
  - Cashflow visualization
  - Account management interface

### Completed Recently
- ✓ Frontend layout foundation
  - Base layout with Material-UI
  - Responsive navigation system
  - Theme configuration
  - Mobile-friendly design

### Planned
- Frontend features implementation
- User authentication
- Mobile applications
- Banking API integration
- Notification system

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
