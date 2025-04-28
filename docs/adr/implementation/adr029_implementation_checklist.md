# ADR-029 Implementation Checklist: Transaction Categorization and Reference System

## Overview

This checklist outlines the steps to implement ADR-029, which introduces a standardized Transaction Reference System to address inconsistencies in transaction categorization, referencing, and matching. The implementation will follow the registry pattern established elsewhere in the codebase.

## Phase 1: Core Registry Components (25%)

- [ ] **Create Core Registry Files**
  - [ ] Create `src/common/transaction_reference_registry.py` with base registry class
  - [ ] Define standard transaction types and field access patterns
  - [ ] Implement key generation methods for contribution factors
  - [ ] Add field extraction utilities for different transaction types
  - [ ] Create proper type hints and documentation

- [ ] **Implement Registry Tests**
  - [ ] Create unit tests for TransactionReferenceRegistry
  - [ ] Test key generation for different transaction types
  - [ ] Test field extraction from various transaction structures
  - [ ] Test edge cases with missing fields
  - [ ] Ensure 100% test coverage for registry functions

- [ ] **Implement Registry Documentation**
  - [ ] Create README.md documenting registry usage patterns
  - [ ] Add comprehensive docstrings to all methods
  - [ ] Create usage examples for common scenarios

## Phase 2: Category Matcher Implementation (25%)

- [ ] **Create CategoryMatcher Service**
  - [ ] Implement CategoryMatcher class in `src/services/category_matcher.py`
  - [ ] Define interface for category matching against transactions
  - [ ] Create helper methods for extracting categories
  - [ ] Implement hierarchical matching for parent-child relationships
  - [ ] Add support for fuzzy matching where appropriate
  - [ ] Integrate with existing CategoryRepository

- [ ] **Enhance CategoryRepository**
  - [ ] Add methods for hierarchical category queries
  - [ ] Implement efficient retrieval of related categories
  - [ ] Create `is_category_or_child` method for testing relationships
  - [ ] Optimize for performance with cached lookups where appropriate

- [ ] **Implement Matcher Tests**
  - [ ] Create unit tests for CategoryMatcher service
  - [ ] Test hierarchical category matching
  - [ ] Test fuzzy matching capabilities
  - [ ] Ensure proper handling of edge cases and null values
  - [ ] Verify consistent performance with large category hierarchies

## Phase 3: Forecast Service Integration (20%)

- [ ] **Update ForecastService**
  - [ ] Modify _calculate_daily_forecast to use TransactionReferenceRegistry
  - [ ] Update contributingFactors key generation with registry methods
  - [ ] Replace hardcoded string matching with CategoryMatcher service
  - [ ] Fix income source vs type key generation
  - [ ] Maintain proper category filtering using CategoryMatcher

- [ ] **Review and Update Tests**
  - [ ] Fix existing test_get_custom_forecast test
  - [ ] Fix test_get_custom_forecast_filtered test
  - [ ] Add new tests for category matching edge cases
  - [ ] Add tests for category filtering with hierarchy

- [ ] **Implement Error Handling**
  - [ ] Add proper error handling for category matching failures
  - [ ] Implement graceful fallbacks for missing category information
  - [ ] Log detailed information about matching issues

## Phase 4: Additional Service Integration (15%)

- [ ] **Update Historical Service**
  - [ ] Refactor transaction processing to use TransactionReferenceRegistry
  - [ ] Update category filtering logic to use CategoryMatcher
  - [ ] Ensure consistent key generation for historical analysis

- [ ] **Update Transaction Service**
  - [ ] Refactor get_day_transactions to support registry-based filtering
  - [ ] Update category filtering to use CategoryMatcher
  - [ ] Ensure consistent field access patterns

- [ ] **Update Analytics Service**
  - [ ] Refactor transaction grouping to use consistent keys
  - [ ] Update category analysis with proper hierarchical support
  - [ ] Ensure trend analysis uses consistent source references

## Phase 5: Testing and Validation (10%)

- [ ] **Integration Testing**
  - [ ] Verify consistent behavior across all impacted services
  - [ ] Test with complex category hierarchies
  - [ ] Validate performance with large transaction volumes
  - [ ] Test filtering with multiple category criteria

- [ ] **System Testing**
  - [ ] End-to-end testing of forecasting flows
  - [ ] Verify consistent behavior with historical analysis
  - [ ] Test category-based filtering in all relevant scenarios

- [ ] **Performance Testing**
  - [ ] Verify acceptable performance with large category hierarchies
  - [ ] Test with high transaction volumes
  - [ ] Validate caching strategies are effective

## Phase 6: Documentation and Knowledge Transfer (5%)

- [ ] **Update Documentation**
  - [ ] Create comprehensive documentation for TransactionReferenceRegistry
  - [ ] Document CategoryMatcher usage patterns
  - [ ] Update relevant service documentation

- [ ] **Knowledge Transfer**
  - [ ] Prepare overview of the new pattern for the team
  - [ ] Create examples demonstrating proper registry usage
  - [ ] Document common pitfalls and best practices

## Completion Criteria

To consider ADR-029 fully implemented, all of the following must be true:

1. All tests are passing, including the previously failing tests
2. The implementation follows the registry pattern established in the ADR
3. No hardcoded string matching remains in transaction category handling
4. Documentation is complete and comprehensive
5. The implementation has been reviewed and approved by team leads

## Dependencies

- Existing CategoryRepository implementation
- Account registry pattern (for reference)
- BaseService pattern for service implementation

## Risks and Mitigations

- **Risk**: Performance impact of hierarchical category matching
  - **Mitigation**: Implement efficient caching strategies

- **Risk**: Breaking changes to existing transaction processing
  - **Mitigation**: Thorough testing and gradual integration

- **Risk**: Complexity increase with additional abstractions
  - **Mitigation**: Comprehensive documentation and examples

## Implementation Notes

1. Follow the registry pattern established for account types
2. Ensure backward compatibility during transition
3. Prioritize fixing immediate issues in ForecastService
4. Use proper error handling and logging throughout
5. Follow established naming conventions for consistency
