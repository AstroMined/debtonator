# ADR-024: Feature Flag System (Revised)

## Status

Proposed (Revision 1)

## Context

During the implementation planning for ADR-019 (Banking Account Types Expansion), we identified a need for a feature flag system to control the rollout of new account types, including multi-currency and international account support. Currently, Debtonator lacks a structured way to manage feature releases, which creates challenges when deploying new functionality:

1. New features must be fully deployed or not deployed at all, without a middle ground
2. No ability to gradually roll out features to specific user segments
3. Limited options for testing features in production environments
4. Difficult to quickly disable problematic features without a full rollback
5. No standardized approach to feature lifecycle management

As we expand Debtonator with more sophisticated functionality like polymorphic account types, multi-currency support, and international banking features, we need a robust feature flag system to manage these changes safely and systematically.

## Decision

We will implement a comprehensive feature flag system for Debtonator that provides:

1. A flexible, configuration-driven approach to enabling/disabling features
2. Support for different flag types: boolean, percentage rollout, user-segment based
3. Runtime toggling of features without application restart
4. Proper persistence of flag states across application restarts
5. Administrative interface for managing feature flags

**Key Architectural Change:** Rather than scattering feature flag checks throughout the codebase, we will implement a layered middleware/interceptor pattern that centralizes feature flag enforcement at well-defined boundaries in our application architecture.

### Feature Flag Types

The system will support the following types of feature flags:

1. **Boolean Flags**: Simple on/off toggles for features across the entire application
2. **Percentage Rollout Flags**: Gradual rollout to a percentage of users
3. **User Segment Flags**: Enable features for specific user segments based on criteria (e.g., admin users, beta testers)
4. **Time-Based Flags**: Automatically enable/disable features based on schedule

### Technical Implementation

#### Core Components

1. **Feature Flag Registry**

The registry remains largely unchanged from the original design:

```python
class FeatureFlagRegistry:
    """Central registry for feature flags and their current state."""
    
    def __init__(self):
        self._flags = {}
        self._observers = []
    
    def register(self, flag_name, flag_type, default_value, description, metadata=None):
        """Register a new feature flag."""
        if flag_name in self._flags:
            raise ValueError(f"Feature flag {flag_name} already registered")
        
        self._flags[flag_name] = {
            "type": flag_type,
            "value": default_value,
            "description": description,
            "metadata": metadata or {},
        }
    
    def get_value(self, flag_name, context=None):
        """Get the current value of a feature flag."""
        if flag_name not in self._flags:
            raise ValueError(f"Unknown feature flag: {flag_name}")
        
        flag = self._flags[flag_name]
        
        # Evaluation logic for different flag types
        # (Same implementation as original)
        
        return flag["value"]
    
    # Other registry methods remain unchanged
```

2. **Feature Flag Service**

The service remains similar to allow checking of flags:

```python
class FeatureFlagService:
    """Service for managing feature flags."""
    
    def __init__(self, registry, storage):
        self.registry = registry
        self.storage = storage
        self._initialize()
    
    def is_enabled(self, flag_name, context=None):
        """Check if a feature flag is enabled."""
        try:
            value = self.registry.get_value(flag_name, context)
            return bool(value)
        except ValueError:
            return False
    
    # Other service methods remain unchanged
```

3. **Domain-Specific Exceptions**

New standardized exceptions for feature flag errors:

```python
class FeatureFlagError(Exception):
    """Base class for feature flag related errors."""
    pass

class FeatureDisabledError(FeatureFlagError):
    """Error raised when attempting to use a disabled feature."""
    
    def __init__(self, feature_name, entity_type=None, entity_id=None):
        self.feature_name = feature_name
        self.entity_type = entity_type
        self.entity_id = entity_id
        
        if entity_type and entity_id:
            message = f"Feature '{feature_name}' is disabled for {entity_type} '{entity_id}'"
        elif entity_type:
            message = f"Feature '{feature_name}' is disabled for {entity_type}"
        else:
            message = f"Feature '{feature_name}' is disabled"
            
        super().__init__(message)
```

4. **Repository Layer Interceptor**

New component that enforces feature flags at the repository layer:

```python
class FeatureFlagRepositoryProxy:
    """
    Proxy that wraps repository objects to enforce feature flag requirements.
    This provides a clean separation between repository logic and feature flag enforcement.
    """
    
    def __init__(self, repository, feature_flag_service, config_provider=None):
        self.repository = repository
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider or DefaultConfigProvider()
        self.operation_requirements = self.config_provider.get_repository_requirements()
        
        # Log configuration on initialization for debugging
        self._log_configuration()
    
    def __getattr__(self, name):
        """
        Intercept attribute access to wrap methods with feature checking.
        Returns the original attribute for non-methods or methods without requirements.
        """
        original_attr = getattr(self.repository, name)
        
        # If not a method or no requirements, return as-is
        if not callable(original_attr) or name not in self.operation_requirements:
            return original_attr
            
        # Create a wrapped method with feature checking
        @functools.wraps(original_attr)
        async def wrapped_method(*args, **kwargs):
            requirements = self.operation_requirements[name]
            
            # Get the account type from args or kwargs
            account_type = None
            if args and len(args) > 0:
                account_type = args[0]
            elif 'account_type' in kwargs:
                account_type = kwargs['account_type']
                
            # Check if we have requirements for this account type
            if isinstance(requirements, dict) and account_type in requirements:
                flags = requirements[account_type]
                for flag in flags:
                    if not self.feature_flag_service.is_enabled(flag):
                        # Raise domain-specific exception
                        raise FeatureDisabledError(
                            flag, 
                            entity_type="account_type", 
                            entity_id=account_type
                        )
            
            # If we get here, either no flags needed or all required flags are enabled
            logger.debug(
                f"Feature flag check passed for {name}({account_type})",
                extra={
                    "repository": self.repository.__class__.__name__,
                    "method": name,
                    "account_type": account_type
                }
            )
            return await original_attr(*args, **kwargs)
            
        return wrapped_method
        
    def _log_configuration(self):
        """Log the proxy configuration for debugging."""
        logger.debug(
            f"FeatureFlagRepositoryProxy initialized for {self.repository.__class__.__name__}",
            extra={"requirements": self.operation_requirements}
        )
```

5. **Configuration Provider**

New component to externalize feature requirements configuration:

```python
class ConfigProvider:
    """Base class for configuration providers."""
    
    def get_repository_requirements(self):
        """Get the repository method requirements."""
        raise NotImplementedError()
        
    def get_service_requirements(self):
        """Get the service method requirements."""
        raise NotImplementedError()
        
    def get_api_requirements(self):
        """Get the API endpoint requirements."""
        raise NotImplementedError()
        
class DefaultConfigProvider(ConfigProvider):
    """Default in-memory configuration provider."""
    
    def get_repository_requirements(self):
        """Get the repository method requirements."""
        return {
            "create_typed_account": {
                "ewa": ["BANKING_ACCOUNT_TYPES_ENABLED"],
                "bnpl": ["BANKING_ACCOUNT_TYPES_ENABLED"],
                "payment_app": ["BANKING_ACCOUNT_TYPES_ENABLED"]
            },
            "update_typed_account": {
                "ewa": ["BANKING_ACCOUNT_TYPES_ENABLED"],
                "bnpl": ["BANKING_ACCOUNT_TYPES_ENABLED"],
                "payment_app": ["BANKING_ACCOUNT_TYPES_ENABLED"]
            },
            "get_by_type": {
                "ewa": ["BANKING_ACCOUNT_TYPES_ENABLED"],
                "bnpl": ["BANKING_ACCOUNT_TYPES_ENABLED"],
                "payment_app": ["BANKING_ACCOUNT_TYPES_ENABLED"]
            }
        }
        
class JsonFileConfigProvider(ConfigProvider):
    """Configuration provider that loads from JSON files."""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self._config = None
        self._load_config()
        
    def _load_config(self):
        """Load configuration from JSON file."""
        with open(self.config_path) as f:
            self._config = json.load(f)
            
    def get_repository_requirements(self):
        """Get the repository method requirements."""
        return self._config.get("repository_requirements", {})
```

6. **Service Layer Interceptor** (Future Phase)

```python
class ServiceInterceptor:
    """
    Intercepts service method calls to enforce feature flag requirements.
    This separates service business logic from feature gating.
    """
    
    def __init__(self, feature_flag_service, config_provider=None):
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider or DefaultConfigProvider()
        self.method_requirements = self.config_provider.get_service_requirements()
    
    async def intercept(self, service, method_name, args, kwargs):
        """
        Intercept service method calls to check feature flags.
        Raises FeatureDisabledError if a required feature is disabled.
        """
        for pattern, flags in self.method_requirements.items():
            if self._matches_pattern(method_name, pattern):
                for flag in flags:
                    if not self.feature_flag_service.is_enabled(flag):
                        raise FeatureDisabledError(flag)
                        
        # Log successful check
        logger.debug(
            f"Feature flag check passed for {method_name}",
            extra={
                "service": service.__class__.__name__,
                "method": method_name
            }
        )
        return True
```

7. **API Middleware** (Final Phase)

```python
class FeatureFlagMiddleware:
    """
    ASGI middleware that enforces feature flag requirements at the API layer.
    This centralizes API-level feature gating in one place.
    """
    
    def __init__(
        self, 
        app, 
        feature_flag_service,
        config_provider=None
    ):
        self.app = app
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider or DefaultConfigProvider()
        self.feature_requirements = self.config_provider.get_api_requirements()
        
    async def __call__(self, request, call_next):
        """ASGI middleware entry point."""
        for pattern, required_flags in self.feature_requirements.items():
            if re.match(pattern, request.url.path):
                for flag in required_flags:
                    if not self.feature_flag_service.is_enabled(flag):
                        # Translate domain exception to HTTP response
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": f"Feature '{flag}' is not enabled",
                                "code": "FEATURE_DISABLED",
                                "path": request.url.path
                            }
                        )
                        
        # Log successful check
        logger.debug(
            f"Feature flag check passed for {request.url.path}",
            extra={"path": request.url.path}
        )
        return await call_next(request)
```

### Integration with Existing Codebase

#### Repository Factory Integration

```python
class RepositoryFactory:
    """Factory for creating repositories with specialized functionality."""
    
    @classmethod
    def create_account_repository(
        cls,
        session: AsyncSession,
        account_type: Optional[str] = None,
        feature_flag_service: Optional[FeatureFlagService] = None,
    ) -> AccountRepository:
        """
        Create an account repository with specialized functionality based on account type.
        
        Args:
            session: SQLAlchemy async session
            account_type: Optional account type to determine specialized functionality
            feature_flag_service: Optional feature flag service for feature validation
            
        Returns:
            AccountRepository with specialized functionality for the given type
        """
        # Create the base repository
        base_repo = AccountRepository(session)
        
        # Load type-specific functionality
        if account_type:
            module_path = cls._get_module_path(account_type)
            if module_path:
                module = cls._get_or_load_module(module_path)
                if module:
                    cls._bind_module_functions(base_repo, module, session)
        
        # If we have a feature flag service, wrap with the proxy
        if feature_flag_service:
            # Use environment-specific config provider
            config_provider = cls._get_config_provider()
            return FeatureFlagRepositoryProxy(base_repo, feature_flag_service, config_provider)
            
        return base_repo
        
    @classmethod
    def _get_config_provider(cls):
        """Get the configuration provider based on environment."""
        env = os.getenv("APP_ENV", "development")
        config_path = f"config/feature_flags_{env}.json"
        
        if os.path.exists(config_path):
            return JsonFileConfigProvider(config_path)
        else:
            return DefaultConfigProvider()
```

### Before and After Examples

#### Current Approach (Before)

```python
# In repository
async def create_typed_account(self, account_type, data, feature_flag_service=None):
    # Check feature flags
    if feature_flag_service and account_type in ["ewa", "bnpl", "payment_app"]:
        if not feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
            raise ValueError(f"Account type '{account_type}' is not available due to feature flags")
    
    # Actual repository logic follows...
    # ...

# In service
async def create_account(self, data):
    account_type = data["account_type"]
    
    # Check feature flags again
    if account_type in ["ewa", "bnpl", "payment_app"]:
        if not self.feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
            raise ValueError(f"Account type '{account_type}' is currently disabled")
    
    # Service logic follows...
    # ...

# In API endpoint
@router.post("/accounts")
async def create_account(account_data: AccountCreate, feature_flag_service = Depends(get_feature_flag_service)):
    # Check feature flags yet again
    if account_data.account_type in ["ewa", "bnpl", "payment_app"]:
        if not feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
            raise HTTPException(status_code=403, detail="This account type is not available")
    
    # Endpoint logic follows...
    # ...
```

#### New Approach (After)

```python
# In repository - NO feature flag checks!
async def create_typed_account(self, account_type, data):
    # Pure repository logic, no feature flag checks
    # ...

# In service - NO feature flag checks!
async def create_account(self, data):
    account_type = data["account_type"]
    
    # Pure business logic, no feature flag checks
    # ...

# In API endpoint - NO feature flag checks!
@router.post("/accounts")
async def create_account(account_data: AccountCreate):
    # Pure endpoint logic, no feature flag checks
    # ...

# Feature flags are enforced by:
# 1. FeatureFlagRepositoryProxy for repository methods
# 2. ServiceInterceptor for service methods
# 3. FeatureFlagMiddleware for API endpoints
```

### Error Handling Strategy

We'll standardize on domain-specific exceptions for feature flag violations:

1. **FeatureFlagError**: Base class for all feature flag related errors
2. **FeatureDisabledError**: Raised when attempting to use a disabled feature
3. **FeatureConfigurationError**: Raised for configuration issues

Each layer will handle these exceptions appropriately:

1. **Repository Layer**: Raises domain exceptions directly
2. **Service Layer**: May catch and transform exceptions as needed
3. **API Layer**: Translates exceptions to appropriate HTTP responses

Example:

```python
# Repository raises domain exception
raise FeatureDisabledError("BANKING_ACCOUNT_TYPES_ENABLED", "account_type", "ewa")

# API exception handler
@app.exception_handler(FeatureDisabledError)
async def feature_disabled_exception_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
            "code": "FEATURE_DISABLED",
            "feature": exc.feature_name
        }
    )
```

### Runtime Flag Propagation

The system will handle runtime flag changes as follows:

1. **Immediate Effect**: Flag changes take effect immediately for new operations
2. **No Impact on In-Progress Operations**: Operations that have already passed feature checks will complete
3. **Observability**: Flag change events will be logged and can trigger notifications
4. **Caching Strategy**: 
   - Flag values are cached in memory for performance
   - Cache has a short TTL (e.g., 30 seconds) to balance performance and freshness
   - Explicit cache invalidation on flag changes

### Implementation Plan

We will implement the feature flag system in a bottom-up approach, aligning with our current refactoring strategy:

1. **Phase 1: Repository Layer Implementation** (1-2 weeks)
   - Specific Tasks:
     - Implement `FeatureFlagError` exception hierarchy
     - Create `ConfigProvider` interface and implementations
     - Implement `FeatureFlagRepositoryProxy`
     - Update `RepositoryFactory` to use the proxy
     - Create configuration for EWA, BNPL, and PaymentApp repositories
   - Priority Repositories:
     - `AccountRepository` (specifically `create_typed_account` method)
     - Fix affected tests in `test_ewa_crud.py` and `test_payment_app_crud.py`
   - Validation:
     - Existing feature flag tests pass with new implementation
     - No scattered feature flag checks in repository methods

2. **Phase 2: Service Layer Implementation** (2-3 weeks)
   - Build on foundation from Phase 1
   - Implement service interceptor pattern
   - Migrate service-layer feature flag checks to interceptor

3. **Phase 3: API Layer Implementation** (1-2 weeks)
   - Add middleware for API-level feature flag enforcement
   - Create consistent HTTP responses for feature flag violations

### Default Feature Flags

The system will be initialized with the following feature flags:

1. `BANKING_ACCOUNT_TYPES_ENABLED`: Controls access to new banking account types (Payment App, BNPL, EWA)
2. `MULTI_CURRENCY_SUPPORT_ENABLED`: Controls support for multiple currencies in accounts
3. `INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED`: Controls support for international banking fields (IBAN, SWIFT, etc.)

These flags will default to `false` in all environments except development, where they may be enabled for testing purposes.

### Testing Approach

Following our "No Mocks" philosophy, we will test with real objects:

1. **Integration Tests**:
   - Test repositories with real proxies and feature flag services
   - Use real database interactions to verify behavior
   - Configure feature flags in test setup

2. **Test Fixtures**:
```python
@pytest_asyncio.fixture
async def feature_flag_service(db_session):
    """Create and initialize a feature flag service for testing."""
    registry = FeatureFlagRegistry()
    
    # Register test flags
    registry.register("BANKING_ACCOUNT_TYPES_ENABLED", "boolean", True, "Test flag")
    registry.register("MULTI_CURRENCY_SUPPORT_ENABLED", "boolean", True, "Test flag")
    
    # Create service with in-memory storage
    storage = InMemoryFeatureFlagStorage()
    service = FeatureFlagService(registry, storage)
    
    return service

@pytest_asyncio.fixture
async def disabled_banking_types_feature_flag_service(feature_flag_service):
    """Feature flag service with banking types disabled."""
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    return feature_flag_service
```

3. **Test Cases**:
```python
async def test_feature_flag_controls_account_creation(
    ewa_repository, 
    disabled_banking_types_feature_flag_service
):
    """Test that feature flags control EWA account creation."""
    # Create schema
    account_schema = create_ewa_account_schema()
    validated_data = account_schema.model_dump()
    
    # Should fail when flag is disabled
    with pytest.raises(FeatureDisabledError) as excinfo:
        await ewa_repository.create_typed_account("ewa", validated_data)
    
    assert "BANKING_ACCOUNT_TYPES_ENABLED" in str(excinfo.value)
```

### Developer Experience

1. **Logging Strategy**:
   - Each proxy/interceptor logs feature checks with structured data
   - Successful checks logged at DEBUG level
   - Failed checks logged at INFO level
   - Configuration loading logged at INFO level

2. **Developer Tooling**:
   - Add admin endpoint to show current feature flag configuration
   - Create CLI tool to toggle feature flags for development
   - Add debugging headers in responses indicating which feature flags were checked

3. **Troubleshooting Guide**:
   - Specific error messages that indicate which feature is disabled
   - Log correlation between feature checks and repository/service operations
   - Configuration validation on application startup

## Consequences

### Positive

1. **Clean Separation of Concerns**: Feature flag logic is centralized at architectural boundaries rather than scattered throughout the codebase
2. **Reduced Boilerplate**: Eliminates repetitive feature flag checking code in repositories and services
3. **Easier Maintenance**: Feature requirements are defined in one place for each layer
4. **Simpler Testing**: Tests can focus on business logic with clear feature flag configurations
5. **Consistent Enforcement**: Feature flags are enforced uniformly at each layer
6. **Externalized Configuration**: Feature requirements can be updated without code changes

### Negative

1. **Learning Curve**: Proxy and interceptor patterns may be less intuitive initially
2. **Debugging Complexity**: Issues might be harder to diagnose when enforcement happens in proxies
3. **Configuration Management**: Need careful management of feature requirements across layers

### Neutral

1. **Performance Impact**: Slight overhead from proxy method wrapping and pattern matching
2. **Clear Boundaries Required**: Features must align well with architectural boundaries
3. **Documentation Need**: Requires clear documentation for future reference

## Performance Impact

The middleware/interceptor approach has a performance profile similar to the original design:

1. **Proxy Wrapping**: Small overhead for method wrapping (typically microseconds)
2. **Pattern Matching**: Minor cost for URL and method pattern matching 
3. **In-Memory Checks**: Flag checking itself remains a fast in-memory operation

The overall impact should remain under 1ms per request, which is negligible compared to database operations.

## Migration Strategy

Since we are only partially through implementing the original design, switching to the new approach has minimal migration cost:

1. **Repository Layer**: Implement proxy pattern and update tests
2. **Remove In-line Checks**: Gradually remove scattered feature flag checks
3. **Documentation**: Update memory bank with the new pattern
4. **Configuration**: Create initial feature flag configuration files

## Success Metrics

We'll measure the success of the feature flag system by:

1. **Reduced Complexity**: Fewer lines of feature flag checking code throughout the codebase
2. **Test Simplification**: Cleaner integration tests for feature flag behavior
3. **Deployment Reliability**: Fewer incidents related to improperly enforced feature flags
4. **Code Quality**: Less duplication of feature flag checking logic

## Related Documents

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-027: Dynamic Pay Period Rules](/code/debtonator/docs/adr/backend/027-dynamic-pay-period-rules.md)
