# ADR-027: Dynamic Pay Period Rules and Income Model Configuration

## Status
Proposed

## Context
Currently, our EWA (Earned Wage Access) account validation enforces rigid constraints, such as requiring "next payday must be on or after pay period end date." This approach faces several challenges:

1. Payment schedules vary widely across companies, industries, and countries
2. Many employers pay on fixed calendar dates regardless of pay period boundaries
3. Some salary employees are paid in advance of period completion
4. Different pay structures (hourly, salary, commission-based) have different timing patterns
5. Hard-coded validation rules enforce a single business logic model that isn't universally applicable

As shown in test failures, these rigid validations create friction for valid use cases and limit our system's flexibility in representing real-world payment scenarios.

## Decision
We will implement a flexible, user-configurable income model framework that:

1. Removes hard-coded validation rules for pay periods and replaces them with a dynamic rules engine
2. Allows users to define their own income models with custom pay period patterns
3. Supports multiple concurrent income sources with different payment schedules
4. Provides pre-configured templates for common payment models (bi-weekly, semi-monthly, monthly, etc.)
5. Separates validation logic from data structures using a pluggable validator approach

## Implementation Details

### Data Model
- Create a new `IncomeModel` entity to define payment frequency patterns
- Add a `PaymentScheduleRule` entity to define validation logic per income source
- Extend `EWAAccount` to reference an income model instead of hard-coding validation
- Use a rule-based system that can evaluate temporal constraints flexibly

### Validation Approach
- Replace hard failure validations with warnings and confidence scores
- Implement a hierarchical validation system:
  - Required validations (technical constraints)
  - Recommended validations (business logic that can be overridden)
  - Custom validations (user-defined rules)

### Dynamic Rule Loading
- Create a registry for payment rule plugins
- Provide a DSL (Domain Specific Language) for expressing payment schedule logic
- Allow rules to be evaluated conditionally based on user configuration

### UI Considerations
- Provide a simplified configuration interface for common payment patterns
- Include an advanced mode for detailed customization
- Visualize payment schedules to aid user understanding

## Short-Term Actions
1. Remove the current validation rule for "next payday must be on or after pay period end date"
2. Add a configuration flag to toggle between strict and flexible validation
3. Document existing validation as a "default model" rather than a universal requirement

## Long-Term Vision
The system will support complex income modeling such as:
- Irregular payment schedules (gig work, seasonal employment)
- Mixed income sources (part-time + freelance)
- Income source transitions (job changes)
- International payment patterns

## Consequences
- **Positive**: Greater flexibility for different user payment patterns
- **Positive**: More accurate financial forecasting based on real-world scenarios
- **Positive**: Reduced friction during account setup and management
- **Negative**: Increased complexity in validation logic
- **Negative**: Potential for users to configure invalid models without strict guardrails

## References
- ADR-012: Service Layer Business Logic Responsibility
- ADR-019: Banking Account Types Expansion
