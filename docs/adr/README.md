# Debtonator Architecture Decision Records (ADRs)

This catalog provides an overview of all Architecture Decision Records for the Debtonator project, organized by category with concise executive summaries.

## ADR Structure

Each ADR in the Debtonator project follows a standardized structure appropriate for its domain:

### Key Details for Backend ADRs

[backend-template.md](backend-template.md) - Template for backend ADRs covering:

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

### Key Details for Frontend ADRs

[frontend-template.md](frontend-template.md) - Template for frontend ADRs covering:

1. **Executive Summary**: A concise overview of the decision suitable for this catalog
2. **Context**: The user experience problem being solved
3. **Decision**: The high-level solution approach
4. **User Stories**: Categorized user requirements
5. **User Interface and Click Paths**: Detailed interaction flows
6. **Wireframes**: UI mockups and diagrams
7. **Technical Details**: Frontend implementation specifics:
   - Architecture Overview
   - Technology Stack
   - Component Structure
   - State Management
   - API Integration
   - Form Validation
   - Performance Optimizations
   - Accessibility Features
   - Security Considerations
8. **Consequences**: Positive, negative, and neutral UX impacts
9. **Quality Considerations**: Ensuring maintainable frontend code
10. **Performance and Resource Considerations**: Frontend performance impact
11. **Development Considerations**: Implementation effort and challenges
12. **Security and Compliance Considerations**: Frontend security requirements
13. **Timeline**: Implementation schedule and milestones
14. **Monitoring & Success Metrics**: UX success criteria
15. **Team Impact**: Effect on teams and operations
16. **Related Documents**: Links to design systems and related ADRs
17. **Notes**: Discussion points and assumptions
18. **Updates**: Revision history

## Backend ADRs

| Number | Title | Status | Executive Summary | Last Updated |
|--------|-------|--------|-------------------|--------------|
| [ADR-004](frontend/004-bills-table-dynamic-accounts.md) | Bills Table Dynamic Account Support | Accepted | This ADR defines the implementation of a dynamic Bills Table component that generates columns based on available user accounts rather than using hard-coded account columns. By removing fixed account references, implementing dynamic column generation, adding support for bill splits visualization, and enhancing mobile responsiveness, this architecture enables flexible bill management across any number of accounts while providing an intuitive user experience for both single and split payments. | 2025-04-21 |
| [ADR-009](backend/009-bills-payments-separation.md) | Bills and Payments Separation | Accepted | Separates bills and payments into distinct entities to enable more flexible payment tracking and better represent one-to-many relationships between bills and payments. This architectural change supports split payments across time periods, different payment sources for the same bill, non-scheduled transactions, and historical payment tracking. The implementation creates a modified double-entry accounting approach with three core entities (bills, payments, payment sources) while maintaining backward compatibility through a phased implementation strategy across all application layers. | 2025-04-20 |
| [ADR-010](backend/010-api-enhancement-strategy.md) | API Enhancement Strategy | Accepted | Establishes a phased approach for enhancing our API layer to fully expose all core application functionality across account management, bill management, bill splits, income tracking, cashflow analysis, and reporting domains. It defines consistent API design standards, implementation requirements, and a sequential enhancement strategy that maintains system stability while systematically expanding capabilities in manageable, domain-focused phases. | 2025-04-19 |
| [ADR-011](backend/011-datetime-standardization.md) | Datetime Standardization | Implemented | Establishes a comprehensive datetime handling standard throughout the Debtonator platform that enforces UTC storage for all datetime values while providing specialized utilities for each architectural layer. It eliminates timezone inconsistencies by storing all timestamps as UTC, centralizing timezone validation in Pydantic schemas, simplifying database operations with naive datetimes, and providing standardized utility functions for timezone-aware business logic and naive database operations. The implementation is fully complete across all 18 models, supported by consistent patterns for inclusive date range handling, cross-database compatibility, and timezone enforcement with thorough docstrings, resulting in a reliable, maintainable datetime system with 100% test coverage. | 2025-04-20 |
| [ADR-012](backend/012-validation-layer-standardization.md) | Validation Layer Standardization | Implemented | Establishes a three-layer validation architecture across the Debtonator platform to create a clear separation of concerns between Pydantic schemas (input/output validation), SQLAlchemy models (data persistence), and services (business logic). It eliminates validation duplication, improves error handling, enhances testability, and provides a consistent approach to data integrity throughout the application. All 18 models have been successfully refactored to comply with this standardized validation approach. | 2025-04-19 |
| [ADR-013](backend/013-decimal-precision-handling.md) | Decimal Precision Handling | Implemented | Establishes a comprehensive two-tier precision model for financial calculations throughout the Debtonator platform that balances accuracy with usability. By using 4 decimal places for database storage and internal calculations while enforcing 2 decimal places at UI/API boundaries, the system prevents cumulative rounding errors while maintaining familiar financial presentation formats. The implementation leverages Pydantic V2's Annotated types with Field constraints to create specialized decimal types (MoneyDecimal, PercentageDecimal) that encapsulate validation rules, includes robust handling for decimal dictionaries, and implements specialized distribution algorithms to solve common financial calculation challenges like the "$100 split three ways" problem. This standardized approach, fully implemented across all 187 identified decimal fields in the system, ensures consistent decimal handling throughout the application with minimal performance impact. | 2025-04-20 |
| [ADR-014](backend/014-repository-layer-for-crud-operations.md) | Repository Layer for CRUD Operations | Accepted | Establishes a repository pattern throughout the Debtonator platform to abstract database operations from business logic, providing a consistent interface for data access. It defines a type-safe base repository with specialized implementations for each model type, creates a standardized approach to validation, transaction management, and polymorphic entity support, and has been fully implemented across all 18 required models with comprehensive testing coverage. | 2025-04-19 |
| [ADR-015](backend/015-default-uncategorized-category.md) | Default Uncategorized Category | Accepted | Introduces a protected system category for uncategorized items to ensure data integrity and simplify categorization workflows. This feature implements an automatically created "Uncategorized" category with a fixed ID that cannot be modified or deleted, which is used as the default when no category is specified. The design strikes a balance between maintaining referential integrity in the database and improving user experience by not forcing premature categorization decisions, while also establishing a foundation for future machine learning-based categorization suggestions. | 2025-04-20 |
| [ADR-016](backend/016-account-type-expansion.md) | Account Type Expansion | Accepted | Establishes a comprehensive polymorphic account model architecture that supports diverse financial account types with specialized attributes and behaviors while maintaining a consistent interface. By implementing a three-tier type hierarchy (categories, types, subtypes), specialized SQLAlchemy models with joined-table inheritance, a dynamic account type registry, and discriminated Pydantic schemas, this foundational architecture enables accurate representation of banking, investment, loan, and bill/utility accounts, resolves inconsistencies in existing code, and creates a future-proof system that scales to dozens of account types with minimal code duplication. | 2025-04-20 |
| [ADR-017](backend/017-payment-source-schema-simplification.md) | Payment Source Schema Simplification | Accepted | Simplifies the payment source schema architecture by eliminating redundant schema definitions and establishing a clear parent-child relationship model for payments and their sources. This change resolves circular dependencies, reduces technical debt, and creates a more intuitive API by removing the standalone `PaymentSourceCreate` schema in favor of a nested approach where payment sources are always created in the context of a payment. The implementation shifts responsibility for payment ID assignment from the schema to the repository layer, resulting in more consistent validation, simplified testing, and clearer domain modeling throughout the application. | 2025-04-20 |
| [ADR-018](backend/018-flexible-income-shortfall-planning.md) | Flexible Income Shortfall Planning | Accepted | Introduces flexible income planning tools to help users visualize and plan for shortfalls with predictive modeling. This architectural decision replaces rigid income requirement calculations with a customizable "Income Planning" system that accommodates diverse financial situations including freelancers, gig workers, multiple income sources, and various tax scenarios. The implementation provides visualization tools for deficit tracking across multiple timeframes, scenario modeling for different earning strategies, and "what-if" analysis capabilities that support personalized financial strategies rather than prescriptive solutions. | 2025-04-20 |
| [ADR-019](backend/019-banking-account-types-expansion.md) | Banking Account Types Expansion | Accepted | Extends the polymorphic account architecture established in ADR-016 by implementing six specialized banking account types: traditional (checking, savings, credit) and modern financial services (payment apps, BNPL, earned wage access). This expansion provides comprehensive support for international banking with flexible account identification, currency handling, and regional variations, while implementing specialized business logic for each type. The implementation follows Debtonator's established architecture patterns with robust type-specific repositories, schemas, and services, enabling accurate representation of both traditional and emerging financial products within a consistent user experience. | 2025-04-20 |
| [ADR-020](backend/020-loan-account-types-expansion.md) | Loan Account Types Expansion | Accepted | Extends the polymorphic account architecture established in ADR-016 by implementing specialized loan account types for personal loans, auto loans, mortgages, and student loans, with a shared base LoanAccount class that captures common loan attributes. This expansion provides comprehensive support for loan-specific features including amortization calculations, payment tracking, interest computation, and specialized fields for various loan types. The implementation enables powerful payoff forecasting, "what-if" scenario analysis, and debt reduction strategy tools, with specialized handling for student loans with forgiveness programs and mortgages with escrow tracking, enhancing Debtonator's ability to serve users with diverse debt management needs. | 2025-04-20 |
| [ADR-021](backend/021-investment-account-types-expansion.md) | Investment Account Types Expansion | Accepted | Extends the polymorphic account architecture established in ADR-016 by implementing specialized investment account types (brokerage, retirement, HSA, cryptocurrency) with a shared base InvestmentAccount class. This expansion introduces a sophisticated investment holdings model to track portfolio composition, performance metrics, and account-specific attributes across diverse investment vehicles. The implementation provides comprehensive support for investment-specific features including contribution tracking, tax-advantaged account management, health expense management, and cryptocurrency tracking, with specialized portfolio visualization and analysis tools, enhancing Debtonator's ability to offer users a complete financial picture that includes their investment assets and strategies. | 2025-04-20 |
| [ADR-022](backend/022-bills-and-obligations-account-types-expansion.md) | Bills and Obligations Account Types | Proposed | Extends the polymorphic account architecture established in ADR-016 by implementing specialized obligation account types for recurring financial commitments including utilities, subscriptions, insurance, taxes, and legal support payments. This expansion provides comprehensive support for obligation-specific features including payment scheduling, due date calculation, payment history tracking, and specialized validation rules for each obligation type. The implementation enables improved cashflow forecasting, payment compliance tracking, and budget planning with specialized handling for varied payment frequencies and obligation-specific attributes, enhancing Debtonator's ability to provide users with a complete financial picture that includes all recurring financial obligations. | 2025-04-20 |
| [ADR-024](backend/024-feature-flags.md) | Feature Flag System | Implemented | Establishes a comprehensive feature flag system using a middleware/interceptor pattern to centralize flag enforcement at well-defined architectural boundaries across the Debtonator platform. It implements a database-driven, runtime-configurable approach that supports boolean, percentage rollout, user-segment, and time-based flags, with clear separation between feature logic and flag enforcement. The system has been fully implemented with minimal performance impact (~10ms per request). | 2025-04-19 |
| [ADR-025](backend/025-statement-types-expansion.md) | Statement Types Expansion | Proposed | Defines a flexible statement model for different account types with support for specialized statement attributes and period-based reporting. This architectural decision implements a polymorphic statement history structure that mirrors the account type hierarchy, allowing for accurate representation of statements across banking, investment, loan, and utility accounts. The implementation provides type-specific validation, specialized fields for different statement types, and a registry-based approach that maintains consistency with the account type system while enabling powerful analytics and reporting capabilities. | 2025-04-20 |
| [ADR-027](backend/027-dynamic-pay-period-rules.md) | Dynamic Pay Period Rules | Accepted | Implements a flexible system for defining and managing complex pay period rules to support diverse income patterns. This architectural decision replaces rigid validation rules with a configurable rule engine that accommodates various payment schedules including fixed calendar dates, advance payments, and different pay structures (hourly, salary, commission-based). The implementation provides a registry for payment rule plugins, a domain-specific language for expressing payment schedule logic, and support for conditional rule evaluation based on user configuration, enabling accurate representation of real-world payment scenarios across different industries, companies, and countries. | 2025-04-20 |

## Frontend ADRs

| Number | Title | Status | Executive Summary | Last Updated |
|--------|-------|--------|-------------------|--------------|
| [ADR-005](frontend/005-bills-table-enhancements.md) | Bills Table UI/UX Enhancements | Accepted | This ADR details the enhancement of the Bills Table component to improve usability and performance, focusing on split payment visualization, mobile responsiveness, performance with large datasets, and visual feedback for payment status. The implementation uses Material-UI DataGrid with custom cell renderers, responsive design patterns, and virtualization for better performance. These improvements enable users to more effectively manage complex bill payments across multiple accounts while maintaining performance on both desktop and mobile devices. | 2025-04-21 |
| [ADR-006](frontend/006-redux-toolkit-state-management.md) | Redux Toolkit State Management | Accepted | Adopts Redux Toolkit as the global state management solution for the Debtonator application with a domain-driven slice architecture (accounts, bills, income, cashflow), type-safe actions and selectors, and performance optimizations through memoization. The implementation provides a centralized source of truth for application state, enables efficient re-renders with complex financial data, and establishes consistent data access patterns throughout the application. | 2025-04-21 |
| [ADR-023](frontend/023-account-types-frontend.md) | Account Types Frontend | Proposed | Defines the frontend implementation for the expanded account type system established in ADRs 016, 019, 020, 021, and 022. It creates a consistent yet flexible architecture for managing diverse account types through reusable components, specialized forms and displays, category-based organization, and integration with existing features like bill splits and cashflow analysis. The implementation provides users with a comprehensive view of their financial situation while maintaining specialized functionality for each account type. | 2025-04-21 |
| [ADR-026](frontend/026-statement-types-frontend.md) | Statement Types Frontend | Proposed | Defines the frontend implementation for the polymorphic statement history structure established in ADR-025. We will create a comprehensive component architecture that renders type-specific information for different statement types through a component registry pattern. This includes specialized visualizations, interaction patterns, and responsive UI components for credit, checking, savings, and other statement types. The implementation integrates with the feature flag system for controlled rollout, follows accessibility best practices, and provides an extensible foundation for future statement types while maintaining consistent user experience across all statement types. | 2025-04-23 |
| [ADR-028](frontend/028-feature-flag-management-frontend.md) | Feature Flag Management Frontend | Proposed | Defines the frontend implementation for a comprehensive feature flag management interface that enables non-technical administrators to control feature rollouts through an intuitive React-based dashboard with toggle controls, percentage rollouts, user segmentation, and requirement management. The interface provides visibility into feature usage and history while maintaining proper separation from the backend implementation established in ADR-024. | 2025-04-20 |

## Archived ADRs

| Number | Title | Status | Executive Summary | Last Updated |
|--------|-------|--------|-------------------|--------------|
| [ADR-001](archive/001-database-schema-design.md) | Database Schema Design | Superseded | Defined the initial database schema design with core entities for accounts, bills, and payments. | - |
| [ADR-002](archive/002-historical-data-entry.md) | Historical Data Entry | Superseded | Established patterns for capturing and managing historical data points for financial analysis. | - |
| [ADR-003](archive/003-dynamic-accounts-and-bill-splits.md) | Dynamic Accounts and Bill Splits | Superseded | Defined the initial approach for linking bills with accounts and implementing bill splits. | - |
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
