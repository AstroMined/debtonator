# Technical Context: Debtonator

## Technology Stack

### Backend
- **Framework**: FastAPI
  - High performance, async Python web framework
  - Automatic OpenAPI documentation
  - Built-in data validation with Pydantic

- **Repository Pattern**:
  - Separates data access logic from business logic
  - Provides a consistent interface for database operations
  - Encapsulates SQLAlchemy-specific implementation details
  - Enables easier testing through dependency injection

- **Database**:
  - Development: SQLite (simple setup, file-based storage)
  - Production: MySQL/MariaDB (robust performance, strong community)

- **Data Validation**: Pydantic
  - Pydantic V2 style validation throughout
  - Type checking and automatic validation
  - Schema-based validation with proper inheritance
  - Comprehensive cross-field validation

### Frontend
- **Framework**: React with TypeScript
  - Component-based architecture
  - Type safety with TypeScript

- **UI Components**: Material-UI
  - Comprehensive component library
  - Responsive design support

- **Form Management**: Formik & Yup
  - Form state management
  - Validation with Yup schemas

## Technical Standards

### Datetime Handling
- All datetime fields use timezone-aware datetime objects
- UTC is used as the standard timezone for stored data
- Conversion to local timezone handled in UI layer

### Validation Architecture
- Three-layer validation approach:
  1. **Schema Layer**: Basic structural validation with Pydantic
  2. **Service Layer**: Business logic validation
  3. **Database Layer**: Data integrity constraints

### Decimal Precision
- Two-tier precision model:
  - 4 decimal places for storage in database (Numeric(12, 4))
  - 2 decimal places for display at UI/API boundaries
- MoneyDecimal type for monetary values
- PercentageDecimal type for percentage values
- Formatting handled consistently across the application

## Data Models

### Core Entity Models
- **Account**: Account types, balances, credit limits
- **Bill/Liability**: Due dates, amounts, categories
- **Payment**: Amount, date, bill reference
- **PaymentSource**: Account allocation for payments
- **BillSplit**: Bill amount distribution across accounts
- **Income**: Sources, amounts, deposit status

### Analysis Models
- **BalanceHistory**: Historical account balance tracking
- **StatementHistory**: Credit account statement tracking
- **CreditLimitHistory**: Changes in available credit
- **Cashflow**: Forecasting, daily deficit calculations
- **Categories**: Hierarchical categorization support

## Technical Constraints

### Data Migration
- Preserve historical data since 2017
- Maintain data integrity during migration
- Handle date format conversions

### Performance Requirements
- Fast cashflow calculations
- Responsive UI updates
- Efficient database queries

### Security Requirements
- Secure user authentication
- Financial data encryption
- Input validation

## Development Setup
1. Python virtual environment with UV
   - Centralized configuration in pyproject.toml
   - Dependency management with UV

2. Node.js for frontend development

3. Development tools:
   - VS Code
   - Git for version control
   - Testing frameworks (pytest)

## Deployment Considerations
1. Database migration strategy
   - Schema versioning
   - Data migration scripts

2. API versioning
   - URL versioning
   - OpenAPI/Swagger docs

3. Frontend deployment
   - Static file hosting
   - Build optimization

4. Monitoring and logging
   - Error tracking
   - Performance monitoring
   - Backup strategy
