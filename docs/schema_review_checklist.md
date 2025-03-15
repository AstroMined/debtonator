# Schema Review Checklist

This document provides a standardized checklist for reviewing schema files to ensure compliance with ADR-011 (Datetime Standardization) and ADR-012 (Validation Layer Standardization), as well as adherence to DRY (Don't Repeat Yourself) and SRP (Single Responsibility Principle) principles.

## ADR-011 Compliance (Datetime Standardization)

### Base Class Inheritance
- [ ] Schema classes inherit from BaseSchemaValidator instead of directly from BaseModel
- [ ] No redundant timezone validation logic is implemented (relies on BaseSchemaValidator)

### Datetime Field Validation
- [ ] All datetime fields are validated for timezone awareness
- [ ] UTC timezone is consistently enforced for all datetime fields
- [ ] No mixing of naive and aware datetime objects

### Type Consistency
- [ ] Consistent use of datetime type with timezone information for date fields
- [ ] Avoids using date type for fields that should have timezone information
- [ ] No inconsistent mixture of date and datetime types for similar fields across schemas

### Documentation
- [ ] All datetime fields have UTC explicitly mentioned in their descriptions
- [ ] Docstrings clearly explain timezone requirements

### Default Values
- [ ] Default values for datetime fields use BaseSchemaValidator's approach
- [ ] No custom default_factory lambdas with ZoneInfo("UTC")
- [ ] Consistent timezone source (timezone.utc vs ZoneInfo("UTC"))

## ADR-012 Compliance (Validation Layer Standardization)

### Pydantic V2 Style
- [ ] Uses Pydantic V2 style with field_validator instead of V1 validator decorator
- [ ] Validator methods include @classmethod decorator
- [ ] Uses ConfigDict instead of Config class
- [ ] No use of deprecated Pydantic V1 features (e.g., conlist)

### Layer Separation
- [ ] No direct imports from models layer (creates own enums or constants)
- [ ] No circular import patterns
- [ ] No database-specific logic in schemas

### Validation Strategy
- [ ] Validation occurs at the schema level (not delegated to models or services)
- [ ] Input validation is structural, not business-logic focused
- [ ] Clear error messages that provide actionable information

### Schema Structure
- [ ] Follows Base/Create/Update/Response pattern consistently
- [ ] Appropriate field constraints using Field()
- [ ] Consistent exception handling in validators

## DRY (Don't Repeat Yourself) Principle

### Code Reuse
- [ ] No duplicate validation logic between related schemas
- [ ] Common field definitions are extracted to shared constants or base classes
- [ ] Similar validators are refactored to shared functions or inherited from base classes

### Field Definitions
- [ ] Field definitions are not duplicated between Base and Update schemas
- [ ] Constraints are consistently applied across all schema variants

### Validator Logic
- [ ] No duplicate validator implementations for the same field type
- [ ] Cross-field validation is defined once and reused where needed

## SRP (Single Responsibility Principle)

### Focus
- [ ] Each schema class has a single, well-defined purpose
- [ ] Validators focus on structural validation, not business rules
- [ ] Complex validation logic is broken down into focused validators

### Separation of Concerns
- [ ] No business logic in validators
- [ ] Database-specific concerns are kept separate from schema validation
- [ ] Presentation concerns (like json_schema_extra) are kept separate from validation logic

### Composition
- [ ] Complex schemas use composition with nested schemas
- [ ] Each nested schema has a clear, focused responsibility
- [ ] No "god objects" that try to do too much

## Documentation and Quality

### Docstrings
- [ ] All schema classes have descriptive docstrings
- [ ] Docstrings explain the purpose and usage of the schema
- [ ] Validator methods have docstrings explaining their validation logic

### Field Descriptions
- [ ] All fields have descriptive comments explaining their purpose
- [ ] Field constraints are documented with clear error messages
- [ ] Examples provided where helpful

### Error Messages
- [ ] All validators provide clear, actionable error messages
- [ ] Error messages are consistent in style and format
- [ ] Error messages explain why validation failed and how to fix it
