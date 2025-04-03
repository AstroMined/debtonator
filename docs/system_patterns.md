# System Patterns: Debtonator

## Core Patterns

### Dynamic Accounts and Bill Split Management

```mermaid
graph TD
    Bills[Bills Table] --> PrimaryAccount[Primary Account]
    Bills --> BillSplits[Bill Splits Table]
    BillSplits --> Accounts[Accounts Table]
    PrimaryAccount --> Accounts
```

- **Primary Account Relationship**: Each bill has a primary account (required)
- **Split Relationships**: Bills can be split across multiple accounts
- **Split Amount Logic**: Primary account amount = total bill amount - sum of splits
- **Auto-Split Creation**: Primary account split is created automatically

#### Validation Rules
1. Split amounts must sum to total bill amount
2. All account references must be valid
3. No negative split amounts allowed
4. Each bill-account combination must be unique (enforced by database constraint)

#### Implementation Pattern
1. Bill creation: 
   - Assign primary account
   - Create splits for non-primary accounts
   - Calculate and create primary account split automatically
2. Bill update:
   - Validate split integrity
   - Update or create splits as needed
   - Recalculate primary account split amount

### Datetime Standardization
```mermaid
graph TD
    A[Datetime Field] --> B[UTC Storage]
    B --> C[Timezone-aware Objects]
    
    C --> D[SQLAlchemy Models]
    C --> E[Pydantic Schemas]
    C --> F[Tests]
    
    G[Frontend] --> H[Local Timezone Display]
    H --> I[UTC Conversion]
    I --> B
```

- Store all datetime values in UTC timezone
- Use timezone-aware objects throughout the system
- Convert to local timezone only at presentation layer
- Validate timezone correctness in schemas

## Repository Patterns

### Repository Architecture
```mermaid
graph TD
    A[Service Layer] --> B[Repository Layer]
    B --> C[Database Layer]
    
    B1[BaseRepository] --> B2[AccountRepository]
    B1 --> B3[BillRepository]
    B1 --> B4[PaymentRepository]
    B1 --> B5[BillSplitRepository]
    B1 --> B6[IncomeRepository]
    
    D[RepositoryFactory] --> B2
    D --> B3
    D --> B4
    D --> B5
    D --> B6
```

- BaseRepository provides generic CRUD operations
- Model-specific repositories extend BaseRepository with specialized methods
- RepositoryFactory manages repository instances for dependency injection
- Each repository focuses on a single model with related operations

### Repository Implementation Pattern

- Generic typing for model and primary key types
- Consistent method signatures across repositories
- Relationship loading with selectinload/joinedload
- Pagination support for large result sets
- Transaction handling for multi-operation consistency

## Validation Patterns

### Multi-Layer Validation Approach

```mermaid
graph TD
    A[Validate Input] --> B[Schema Validation]
    B --> C[Service Validation]
    C --> D[Repository Operations]
    
    B1[Schema Rules] --> B2[Field Constraints]
    B1 --> B3[Cross-Field Validation]
    B1 --> B4[Type Conversion]
    
    C1[Service Rules] --> C2[Business Logic]
    C1 --> C3[Relationship Validation]
    C1 --> C4[State Validation]
```

- Schema Layer: Field constraints, type validation, basic cross-field validation
- Service Layer: Business rules, complex validation, state-dependent validation
- Repository Layer: Data access without validation logic
- Clear separation of validation responsibilities between layers

### Decimal Precision Strategy

- Two-tier precision model:
  - 4 decimal places for storage in database (Numeric(12, 4))
  - 2 decimal places for display at UI/API boundaries
- MoneyDecimal type for monetary values (2 decimal places)
- PercentageDecimal type for percentage values (4 decimal places)
- Annotated types with Field constraints for validation

## Service Patterns

### Pattern Analysis

```mermaid
graph TD
    A[Input Data] --> B[Pattern Detection]
    B --> C[Confidence Scoring]
    
    B1[Pattern Types] --> B2[Regular]
    B1 --> B3[Irregular]
    B1 --> B4[Seasonal]
    
    C1[Confidence Factors] --> C2[Sample Size]
    C1 --> C3[Consistency]
    C1 --> C4[Recency]
```

- Financial pattern detection for bills, income, and payments
- Confidence scoring based on sample size and consistency
- Pattern types classified as regular, irregular, or seasonal
- History-based analyses for predictions

## Error Handling Patterns

### Layered Error Handling

- Service Layer: Business logic errors with context
- Repository Layer: Data access errors with details
- API Layer: User-friendly error messages with codes
- Clear error hierarchies with consistent structure

## Testing Patterns

### Integration-First Approach with Real Objects

```mermaid
graph TD
    A[Test] --> B[Real Objects]
    B --> C[Real Database]
    B --> D[Real Repositories]
    B --> E[Real Schemas]
    
    F[Test Philosophy] --> G[No Mocks]
    F --> H[Integration Tests]
    F --> I[Cross-Layer Validation]
    F --> J[Test Database per Test]
```

- **No Mocks Policy**: Strictly prohibit using unittest.mock, MagicMock, or any other mocking libraries
- Integration tests for services with real database that resets between tests
- Cross-layer integration to verify actual interactions between components
- Repository tests with real database fixtures
- API tests for endpoint validation with real service and repository implementations
- Error case testing for validation scenarios
- Service tests with real repositories connected to test database

## Database Patterns

### Model Relationships

- Clear relationship definitions with back_populates
- Proper cascade behavior for related records
- Efficient joins for relationship loading
- Type-safe relationship references

## Model Registration & Circular Reference Resolution

```mermaid
graph TD
    A[SQLAlchemy Models] --> B[String References]
    A --> C[Central Registration]
    
    B --> D[Runtime Resolution]
    C --> E[Controlled Import Order]
    
    D --> F[Circular Reference Resolution]
    E --> F
    
    G[System Initialization] --> H[Repository-Based]
    H --> I[Service-Based]
    I --> J[Database Seeding]
```

### Model Layer Circular Reference Resolution

The model layer uses two key patterns to handle circular dependencies between model files:

#### String Reference Pattern
- Use string references in relationship definitions: `relationship("ModelName", ...)`
- Defer class resolution until runtime rather than import time
- Allows cross-referencing between models without direct imports
- Example: `bills: Mapped[List["Liability"]] = relationship("Liability", back_populates="category")`

#### Central Registration Pattern
- Import all models in controlled order in `models/__init__.py`
- Define explicit dependency order for model registration
- Create a single import path for database initialization
- Ensures all model references are resolved properly at runtime

### System Initialization Pattern

System initialization follows a layered architectural approach:

#### Repository-Based Data Access
- All database access happens exclusively through repository layer
- Even during initialization, direct DB access is prohibited
- Leverages existing repository methods for data operations
- Maintains architectural consistency throughout codebase

#### System Initialization Service
- Dedicated service layer for system data initialization
- Clear separation between schema creation and data seeding
- Ensures all required system data exists on startup
- Example: `ensure_system_categories()` for default category creation

#### Database Initialization Flow
1. Schema creation through SQLAlchemy metadata
2. Repository instantiation with database session
3. Service-based initialization of required system data
4. Validation of system requirements before application start

This approach solves circular dependencies while maintaining architectural integrity by:
1. Using string references for model relationships
2. Centralizing model registration in a single location
3. Leveraging repository layer for all data access
4. Separating schema creation from system data initialization
5. Using service layer for business logic, even during initialization

## Frontend Integration Patterns

### API Client

- Consistent error handling across requests
- Response formatting with appropriate precision
- Type-safe request and response handling
- Loading state management
