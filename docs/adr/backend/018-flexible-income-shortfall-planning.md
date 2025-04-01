# ADR-018: Flexible Income Shortfall Planning

## Status

Proposed

## Context

The original financial management system was designed with specific income calculation features:
- Daily deficit
- Yearly deficit
- Extra income needed (with tax consideration)
- Hourly rate needed at different work hours (40/30/20 per week)

These calculations were designed around a specific personal use case where one household member works part-time to make up budget shortfalls. This approach is too rigid for a general audience with diverse income situations, work arrangements, and financial goals.

As we reposition Debtonator as a broader financial empowerment platform, we need more flexible approaches to income planning that accommodate various user scenarios:
- Freelancers with variable income
- Multiple income sources
- Side businesses and gig economy work
- Passive income streams
- Various tax situations
- Different working hour preferences
- Diverse household financial arrangements

## Decision

We will replace the rigid income requirement calculations with a more flexible "Income Planning" system that:

1. Maintains core deficit tracking across multiple timeframes (daily/weekly/monthly/yearly)
2. Replaces fixed hourly rate calculations with a customizable "Side Gig Calculator" that allows users to:
   - Create multiple earning scenarios
   - Set custom hourly rates, hours worked, and tax considerations
   - Visualize the impact of additional income on their financial outlook
   - Compare different income strategies
3. Provides visualization tools to show how various earning scenarios affect deficit reduction
4. Allows for more personalized income planning rather than prescriptive solutions
5. Enables "what-if" scenario planning for various income adjustments

## Consequences

### Positive

- More inclusive design that addresses diverse financial situations
- Greater flexibility for users to model their unique income arrangements
- Better alignment with the broader vision of financial empowerment
- Supports users in developing personalized financial strategies
- More relevant to a wider audience
- Creates foundation for future community-based features that leverage diverse income approaches

### Negative

- Increased design complexity compared to the original fixed calculations
- Additional UI/UX work to create intuitive scenario planning tools
- More complex data models to support various income scenarios
- Potential for user confusion if income planning tools aren't well-designed

### Neutral

- Requires refactoring of existing income calculation code
- Changes to data models for income tracking and projections
- Updates to UI for deficit visualization

## Implementation Plan

1. Retain core deficit tracking functionality across all timeframes
2. Create new "Income Planning" data models to support:
   - Multiple income scenarios
   - Customizable parameters (hourly rates, hours, tax rates)
   - Scenario comparison
3. Design new UI components for:
   - Scenario creation and management
   - Visual comparison of scenarios
   - Impact visualization on overall financial health
4. Update API endpoints to support new flexible calculations
5. Enhance the cashflow forecast system to incorporate various income scenarios
6. Update tests to validate the new flexible approach

## Notes

This change represents a shift from a personal financial tool to a more broadly applicable platform that empowers users to develop their own financial strategies rather than prescribing specific approaches. It aligns with our vision of creating tools that give users greater agency over their financial lives.
