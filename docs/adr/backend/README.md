# Backend Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) that specifically relate to backend implementation decisions in the Debtonator project.

## Backend ADR Template

Backend ADRs follow a comprehensive template ([backend-template.md](../backend-template.md)) that focuses on:

1. **Business Problem**: The issue motivating the decision
2. **Technical Details**: Implementation across all architectural layers
3. **Data Layer**: Models, repositories, and database changes
4. **Business Logic**: Schemas and services
5. **API Layer**: Endpoints and security
6. **Cross-Cutting Concerns**: Configuration, utilities, and error handling
7. **Performance**: System performance and resource implications
8. **Implementation Impact**: Changes required across the codebase

## Current Backend ADRs

### Core Financial Operations

- **[ADR-009](009-bills-payments-separation.md)**: Bills and Payments Separation - Separates bills and payments into distinct entities for flexible tracking
- **[ADR-018](018-flexible-income-shortfall-planning.md)**: Flexible Income Shortfall Planning - Introduces predictive modeling for income planning

### Data Architecture

- **[ADR-011](011-datetime-standardization.md)**: Datetime Standardization - Establishes UTC datetime handling standards
- **[ADR-012](012-validation-layer-standardization.md)**: Validation Layer Standardization - Creates a three-layer validation architecture
- **[ADR-013](013-decimal-precision-handling.md)**: Decimal Precision Handling - Defines two-tier precision model for financial calculations
- **[ADR-014](014-repository-layer-for-crud-operations.md)**: Repository Layer - Abstracts database operations from business logic
- **[ADR-015](015-default-uncategorized-category.md)**: Default Uncategorized Category - Implements protected system category for uncategorized items

### Account Type System

- **[ADR-016](016-account-type-expansion.md)**: Account Type Expansion - Establishes polymorphic account model architecture
- **[ADR-019](019-banking-account-types-expansion.md)**: Banking Account Types - Implements specialized banking account types
- **[ADR-020](020-loan-account-types-expansion.md)**: Loan Account Types - Implements specialized loan account types
- **[ADR-021](021-investment-account-types-expansion.md)**: Investment Account Types - Implements specialized investment types
- **[ADR-022](022-bills-and-obligations-account-types-expansion.md)**: Bills and Obligations Types - Implements specialized obligation types

### System Infrastructure

- **[ADR-024](024-feature-flags.md)**: Feature Flag System - Creates middleware/interceptor pattern for feature control
- **[ADR-027](027-dynamic-pay-period-rules.md)**: Dynamic Pay Period Rules - Implements flexible system for complex pay period rules

### API and Integration

- **[ADR-010](010-api-enhancement-strategy.md)**: API Enhancement Strategy - Defines phased approach for API layer expansion
- **[ADR-017](017-payment-source-schema-simplification.md)**: Payment Source Schema Simplification - Eliminates redundant schema definitions
- **[ADR-025](025-statement-types-expansion.md)**: Statement Types Expansion - Defines flexible statement model for account types

## Best Practices

When creating new backend ADRs:

1. Follow the standardized template structure
2. Document impact across all architectural layers
3. Include performance considerations with metrics
4. Address security and compliance requirements
5. Provide implementation timelines and phases
6. Define clear success metrics
7. Document team impact and responsibilities

## Related Documents

- [ADR Template - Backend](../backend-template.md)
- [ADR Template - Frontend](../frontend-template.md)
- [System Patterns](/code/debtonator/docs/system_patterns.md)
- [Technical Context](/code/debtonator/docs/tech_context.md)
