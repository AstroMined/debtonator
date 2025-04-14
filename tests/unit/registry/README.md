# Unit Tests for Registry Components

This directory contains unit tests for registry components used throughout the Debtonator application. Registry components provide centralized management of type mappings, feature flags, and other configuration elements.

## Purpose

Registry tests serve to verify:

1. **Registration Functionality**: Test adding entries to registries
2. **Lookup Operations**: Test retrieving entries from registries
3. **Default Handling**: Test fallback and default value behavior
4. **Error Cases**: Test behavior when entries don't exist
5. **Validation**: Test entry validation during registration

## Test Files

```tree
registry/
├── test_account_type_registry.py      # Tests for account type registry
└── test_feature_flag_registry.py      # Tests for feature flag registry
```

## Testing Focus Areas

### Account Type Registry

The `test_account_type_registry.py` file tests the account type registry which maps account types to their model and schema classes:

```python
def test_account_type_registration():
    """Test registering and retrieving account types."""
    registry = AccountTypeRegistry()
    
    # Register a test account type
    registry.register_type(
        type_name="test_account",
        model_class=TestAccount,
        schema_class=TestAccountSchema,
        response_class=TestAccountResponse
    )
    
    # Test retrieving the registered classes
    assert registry.get_model_class("test_account") == TestAccount
    assert registry.get_schema_class("test_account") == TestAccountSchema
    assert registry.get_response_class("test_account") == TestAccountResponse
    
    # Test non-existent type
    with pytest.raises(KeyError):
        registry.get_model_class("nonexistent_type")
```

### Feature Flag Registry

The `test_feature_flag_registry.py` file tests the feature flag registry which manages feature flag state:

```python
def test_feature_flag_registration():
    """Test registering and checking feature flags."""
    registry = FeatureFlagRegistry()
    
    # Register a test feature flag
    registry.register_flag(
        name="test_feature",
        default=False,
        description="A test feature flag"
    )
    
    # Test default value
    assert registry.is_enabled("test_feature") is False
    
    # Enable the flag and test again
    registry.enable_flag("test_feature")
    assert registry.is_enabled("test_feature") is True
    
    # Test non-existent flag
    with pytest.raises(KeyError):
        registry.is_enabled("nonexistent_flag")
```

## Registry Integration with Feature Flags

Feature flags and registry components are closely integrated:

```python
def test_registry_feature_flag_integration():
    """Test integration between registry and feature flags."""
    feature_registry = FeatureFlagRegistry()
    account_registry = AccountTypeRegistry()
    
    # Register feature flags
    feature_registry.register_flag("banking_accounts", default=True)
    feature_registry.register_flag("bnpl_accounts", default=False)
    
    # Register account types
    account_registry.register_type(
        type_name="checking",
        model_class=CheckingAccount,
        schema_class=CheckingAccountSchema,
        response_class=CheckingAccountResponse,
        required_flags=["banking_accounts"]  # Requires banking_accounts flag
    )
    
    account_registry.register_type(
        type_name="bnpl",
        model_class=BNPLAccount,
        schema_class=BNPLAccountSchema,
        response_class=BNPLAccountResponse,
        required_flags=["bnpl_accounts"]  # Requires bnpl_accounts flag
    )
    
    # Test retrieving enabled types
    enabled_types = account_registry.get_enabled_types(feature_registry)
    assert "checking" in enabled_types  # Should be enabled
    assert "bnpl" not in enabled_types  # Should be disabled
    
    # Enable BNPL and test again
    feature_registry.enable_flag("bnpl_accounts")
    enabled_types = account_registry.get_enabled_types(feature_registry)
    assert "checking" in enabled_types  # Still enabled
    assert "bnpl" in enabled_types      # Now enabled
```

## Best Practices

1. **Test Registry CRUD Operations**: Test adding, retrieving, updating, and removing entries
2. **Test Default Handling**: Verify default values are used when appropriate
3. **Test Error Cases**: Ensure proper errors are raised for invalid operations
4. **Test Registry Integration**: Test integration with services and other components
5. **Follow ADRs**: Ensure tests comply with ADRs (especially ADR-024 for feature flags)
