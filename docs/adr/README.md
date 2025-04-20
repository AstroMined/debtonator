# Debtonator Architecture Decision Records (ADRs)

This catalog provides an overview of all Architecture Decision Records for the Debtonator project, organized by category with concise executive summaries.

## ADR Structure

Each ADR in the Debtonator project follows a standardized structure that ensures comprehensive coverage of all architectural layers and considerations:

1. **Executive Summary**: A concise overview of the decision suitable for this catalog
2. **Context**: The problem being solved and relevant constraints
3. **Decision**: The high-level solution approach
4. **Technical Details**: Implementation details for each architectural layer:
   - Architecture Overview
   - Data Layer (Models and Repositories)
   - Business Logic Layer (Schemas and Services)
   - API Layer
   - Frontend Considerations
   - Config, Utils, and Cross-Cutting Concerns
   - Dependencies and External Systems
   - Implementation Impact
5. **Consequences**: Positive, negative, and neutral impacts
6. **Quality Considerations**: How the change improves code quality and prevents tech debt
7. **Performance and Resource Considerations**: Impact on system performance and resources
8. **Development Considerations**: Implementation effort and challenges
9. **Security and Compliance Considerations**: Security implications and requirements
10. **Timeline**: Implementation schedule and milestones
11. **Monitoring & Success Metrics**: How success will be measured
12. **Team Impact**: Effect on teams and operations
13. **Related Documents**: Links to related documentation
14. **Notes**: Discussion points and assumptions
15. **Updates**: Revision history

## Backend ADRs

| Number | Title | Status | Executive Summary | Last Updated |
|--------|-------|--------|-------------------|--------------|
| [ADR-009](backend/009-bills-payments-separation.md) | Bills and Payments Separation | Accepted | Separates bills and payments into distinct entities to enable more flexible payment tracking and better represent one-to-many relationships between bills and payments. | - |
| [ADR-010](backend/010-api-enhancement-strategy.md) | API Enhancement Strategy | Accepted | Establishes a phased approach for enhancing our API layer to fully expose all core application functionality across account management, bill management, bill splits, income tracking, cashflow analysis, and reporting domains. It defines consistent API design standards, implementation requirements, and a sequential enhancement strategy that maintains system stability while systematically expanding capabilities in manageable, domain-focused phases. | 2025-04-19 |
| [ADR-011](backend/011-datetime-standardization.md) | Datetime Standardization | Implemented | Establishes a comprehensive datetime handling standard throughout the Debtonator platform that enforces UTC storage for all datetime values while providing specialized utilities for each architectural layer. It eliminates timezone inconsistencies by storing all timestamps as UTC, centralizing timezone validation in Pydantic schemas, simplifying database operations with naive datetimes, and providing standardized utility functions for timezone-aware business logic and naive database operations. The implementation is fully complete across all 18 models, supported by consistent patterns for inclusive date range handling, cross-database compatibility, and timezone enforcement with thorough docstrings, resulting in a reliable, maintainable datetime system with 100% test coverage. | 2025-04-20 |
| [ADR-012](backend/012-validation-layer-standardization.md) | Validation Layer Standardization | Implemented | Establishes a three-layer validation architecture across the Debtonator platform to create a clear separation of concerns between Pydantic schemas (input/output validation), SQLAlchemy models (data persistence), and services (business logic). It eliminates validation duplication, improves error handling, enhances testability, and provides a consistent approach to data integrity throughout the application. All 18 models have been successfully refactored to comply with this standardized validation approach. | 2025-04-19 |
| [ADR-013](backend/013-decimal-precision-handling.md) | Decimal Precision Handling | Implemented | Establishes a comprehensive two-tier precision model for financial calculations throughout the Debtonator platform that balances accuracy with usability. By using 4 decimal places for database storage and internal calculations while enforcing 2 decimal places at UI/API boundaries, the system prevents cumulative rounding errors while maintaining familiar financial presentation formats. The implementation leverages Pydantic V2's Annotated types with Field constraints to create specialized decimal types (MoneyDecimal, PercentageDecimal) that encapsulate validation rules, includes robust handling for decimal dictionaries, and implements specialized distribution algorithms to solve common financial calculation challenges like the "$100 split three ways" problem. This standardized approach, fully implemented across all 187 identified decimal fields in the system, ensures consistent decimal handling throughout the application with minimal performance impact. | 2025-04-20 |
| [ADR-014](backend/014-repository-layer-for-crud-operations.md) | Repository Layer for CRUD Operations | Accepted | Establishes a repository pattern throughout the Debtonator platform to abstract database operations from business logic, providing a consistent interface for data access. It defines a type-safe base repository with specialized implementations for each model type, creates a standardized approach to validation, transaction management, and polymorphic entity support, and has been fully implemented across all 18 required models with comprehensive testing coverage. | 2025-04-19 |
| [ADR-015](backend/015-default-uncategorized-category.md) | Default Uncategorized Category | Accepted | Introduces a protected system category for uncategorized items to ensure data integrity and simplify categorization workflows. | - |
| [ADR-016](backend/016-account-type-expansion.md) | Account Type Expansion | Accepted | Establishes a comprehensive polymorphic account model architecture that supports diverse financial account types with specialized attributes and behaviors while maintaining a consistent interface. By implementing a three-tier type hierarchy (categories, types, subtypes), specialized SQLAlchemy models with joined-table inheritance, a dynamic account type registry, and discriminated Pydantic schemas, this foundational architecture enables accurate representation of banking, investment, loan, and bill/utility accounts, resolves inconsistencies in existing code, and creates a future-proof system that scales to dozens of account types with minimal code duplication. | 2025-04-20 |
| [ADR-017](backend/017-payment-source-schema-simplification.md) | Payment Source Schema Simplification | Accepted | Simplifies the payment source schema to reduce complexity and improve performance for payment allocation tracking. | - |
| [ADR-018](backend/018-flexible-income-shortfall-planning.md) | Flexible Income Shortfall Planning | Accepted | Introduces flexible income planning tools to help users visualize and plan for shortfalls with predictive modeling. | - |
| [ADR-019](backend/019-banking-account-types-expansion.md) | Banking Account Types Expansion | Accepted | Extends the polymorphic account architecture established in ADR-016 by implementing six specialized banking account types: traditional (checking, savings, credit) and modern financial services (payment apps, BNPL, earned wage access). This expansion provides comprehensive support for international banking with flexible account identification, currency handling, and regional variations, while implementing specialized business logic for each type. The implementation follows Debtonator's established architecture patterns with robust type-specific repositories, schemas, and services, enabling accurate representation of both traditional and emerging financial products within a consistent user experience. | 2025-04-20 |
| [ADR-020](backend/020-loan-account-types-expansion.md) | Loan Account Types Expansion | Accepted | Extends the polymorphic account architecture established in ADR-016 by implementing specialized loan account types for personal loans, auto loans, mortgages, and student loans, with a shared base LoanAccount class that captures common loan attributes. This expansion provides comprehensive support for loan-specific features including amortization calculations, payment tracking, interest computation, and specialized fields for various loan types. The implementation enables powerful payoff forecasting, "what-if" scenario analysis, and debt reduction strategy tools, with specialized handling for student loans with forgiveness programs and mortgages with escrow tracking, enhancing Debtonator's ability to serve users with diverse debt management needs. | 2025-04-20 |
| [ADR-021](backend/021-investment-account-types-expansion.md) | Investment Account Types Expansion | Accepted | Extends the polymorphic account architecture established in ADR-016 by implementing specialized investment account types (brokerage, retirement, HSA, cryptocurrency) with a shared base InvestmentAccount class. This expansion introduces a sophisticated investment holdings model to track portfolio composition, performance metrics, and account-specific attributes across diverse investment vehicles. The implementation provides comprehensive support for investment-specific features including contribution tracking, tax-advantaged account management, health expense management, and cryptocurrency tracking, with specialized portfolio visualization and analysis tools, enhancing Debtonator's ability to offer users a complete financial picture that includes their investment assets and strategies. | 2025-04-20 |
| [ADR-022](backend/022-bills-and-obligations-account-types-expansion.md) | Bills and Obligations Account Types | Proposed | Extends the polymorphic account architecture established in ADR-016 by implementing specialized obligation account types for recurring financial commitments including utilities, subscriptions, insurance, taxes, and legal support payments. This expansion provides comprehensive support for obligation-specific features including payment scheduling, due date calculation, payment history tracking, and specialized validation rules for each obligation type. The implementation enables improved cashflow forecasting, payment compliance tracking, and budget planning with specialized handling for varied payment frequencies and obligation-specific attributes, enhancing Debtonator's ability to provide users with a complete financial picture that includes all recurring financial obligations. | 2025-04-20 |
| [ADR-024](backend/024-feature-flags.md) | Feature Flag System | Implemented | Establishes a comprehensive feature flag system using a middleware/interceptor pattern to centralize flag enforcement at well-defined architectural boundaries across the Debtonator platform. It implements a database-driven, runtime-configurable approach that supports boolean, percentage rollout, user-segment, and time-based flags, with clear separation between feature logic and flag enforcement. The system has been fully implemented with minimal performance impact (~10ms per request). | 2025-04-19 |
| [ADR-025](backend/025-statement-types-expansion.md) | Statement Types Expansion | Proposed | Defines a flexible statement model for different account types with support for specialized statement attributes and period-based reporting. | - |
| [ADR-027](backend/027-dynamic-pay-period-rules.md) | Dynamic Pay Period Rules | Proposed | Implements a flexible system for defining and managing complex pay period rules to support diverse income patterns. | - |

## Frontend ADRs

| Number | Title | Status | Executive Summary | Last Updated |
|--------|-------|--------|-------------------|--------------|
| [ADR-006](archive/006-redux-toolkit-state-management.md) | Redux Toolkit State Management | Accepted | Adopts Redux Toolkit for state management with domain-driven slice architecture for improved performance and maintainability. | - |
| [ADR-023](frontend/INCOMPLETE-023-account-types-frontend.md) | Account Types Frontend | Incomplete | Defines the frontend implementation for displaying and managing the expanded account type system with specialized interfaces for each type. | - |
| [ADR-026](frontend/026-statement-types-frontend.md) | Statement Types Frontend | Proposed | Designs the frontend interface for viewing and managing different statement types with specialized visualizations and interactions. | - |
| [ADR-028](frontend/028-feature-flag-management-frontend.md) | Feature Flag Management Frontend | Proposed | Creates a user-friendly interface for managing feature flags to enable non-technical administrators to control feature rollout. | - |

## Archived ADRs

| Number | Title | Status | Executive Summary | Last Updated |
|--------|-------|--------|-------------------|--------------|
| [ADR-001](archive/001-database-schema-design.md) | Database Schema Design | Superseded | Defined the initial database schema design with core entities for accounts, bills, and payments. | - |
| [ADR-002](archive/002-historical-data-entry.md) | Historical Data Entry | Superseded | Established patterns for capturing and managing historical data points for financial analysis. | - |
| [ADR-003](archive/003-dynamic-accounts-and-bill-splits.md) | Dynamic Accounts and Bill Splits | Superseded | Defined the initial approach for linking bills with accounts and implementing bill splits. | - |
| [ADR-004](archive/004-bills-table-dynamic-accounts.md) | Bills Table Dynamic Accounts | Superseded | Enhanced the bills table to support dynamic account associations for flexible bill management. | - |
| [ADR-005](archive/005-bills-table-enhancements.md) | Bills Table Enhancements | Superseded | Added features to the bills table for improved usability and data tracking capabilities. | - |
| [ADR-007](archive/007-bulk-import-functionality.md) | Bulk Import Functionality | Superseded | Defined patterns for importing financial data in bulk from various sources. | - |
| [ADR-008](archive/008-bill-splits-implementation.md) | Bill Splits Implementation | Superseded | Detailed the implementation approach for splitting bills across multiple accounts. | - |

## Implementation Checklists

These documents track the implementation progress of specific ADRs:

| Document | Related ADR | Description |
|----------|-------------|-------------|
| [ADR-016 Implementation Checklist](implementation/adr016-implementation-checklist.md) | ADR-016 | Tracks the implementation of the polymorphic account type architecture foundation. |
| [ADR-019 Implementation Checklist](implementation/adr019-implementation-checklist.md) | ADR-019 | Tracks the implementation of banking account types expansion. |
| [ADR-024 Implementation Checklist](implementation/adr024-implementation-checklist.md) | ADR-024 | Tracks the implementation of the feature flag system. |

## Compliance Documentation

| Document | Related ADR | Description |
|----------|-------------|-------------|
| [ADR-011 Compliance](compliance/adr-011-compliance.md) | ADR-011 | Documents compliance with the datetime standardization requirements across the codebase. |
