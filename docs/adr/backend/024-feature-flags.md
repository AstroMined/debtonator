# ADR-024: Feature Flag System (Revised)

## Status

Proposed (Revision 2)

## Context

During the implementation planning for ADR-019 (Banking Account Types Expansion), we identified a need for a feature flag system to control the rollout of new account types, including multi-currency and international account support. Currently, Debtonator lacks a structured way to manage feature releases, which creates challenges when deploying new functionality.

Our initial design for the feature flag system (Revision 1) proposed a middleware/interceptor pattern to centralize feature flag enforcement at well-defined boundaries in our application architecture, with feature flag requirements defined in JSON configuration files. However, upon further consideration, we've determined that a fully database-driven approach would be more sustainable and better aligned with our existing implementation that already uses database storage for feature flag values.

## Decision

We will implement a comprehensive feature flag system for Debtonator that provides:

1. A flexible, database-driven approach to enabling/disabling features
2. Support for different flag types: boolean, percentage rollout, user-segment based
3. Runtime toggling of features without application restart
4. Proper persistence of flag states across application restarts
5. Database storage for both flag values AND requirements mapping
6. Well-defined API for frontend management (detailed in ADR-028)

**Key Architectural Change:** Rather than scattering feature flag checks throughout the codebase, we will implement a layered middleware/interceptor pattern that centralizes feature flag enforcement at well-defined boundaries in our application architecture. Both feature flag values and the mapping of which methods require which flags will be stored in the database, allowing for runtime configuration without application restarts.

### Feature Flag Types

The system will support the following types of feature flags:

1. **Boolean Flags**: Simple on/off toggles for features across the entire application
2. **Percentage Rollout Flags**: Gradual rollout to a percentage of users
3. **User Segment Flags**: Enable features for specific user segments based on criteria (e.g., admin users, beta testers)
4. **Time-Based Flags**: Automatically enable/disable features based on schedule

### Technical Implementation

#### Core Components

1. **Feature Flag Model Update**

We will update the existing `FeatureFlag` model to store both flag values and requirements:

```python
class FeatureFlag(Base):
    """Database model for feature flags."""
    
    __tablename__ = "feature_flags"
    
    name = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    requirements = Column(JSON, nullable=True)  # Which methods require this flag
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<FeatureFlag name={self.name} value={self.value} requirements={self.requirements}>"
```

2. **Feature Flag Repository**

The repository will provide methods for both flag values and requirements:

```python
class FeatureFlagRepository(BaseRepository):
    """Repository for feature flag operations."""
    
    def __init__(self, db_session):
        super().__init__(db_session)
        self.model_class = FeatureFlag
    
    async def get_requirements(self, flag_name):
        """Get the requirements for a specific feature flag."""
        flag = await self.get_by_id(flag_name)
        if flag and flag.requirements:
            return flag.requirements
        return {}
    
    async def update_requirements(self, flag_name, requirements):
        """Update the requirements for a feature flag."""
        flag = await self.get_by_id(flag_name)
        if not flag:
            raise ValueError(f"Feature flag {flag_name} does not exist")
        
        flag.requirements = requirements
        await self.session.commit()
        return flag
        
    async def get_all_requirements(self):
        """Get requirements for all feature flags."""
        flags = await self.get_all()
        return {flag.name: flag.requirements for flag in flags if flag.requirements}
```

3. **Database-Driven Config Provider**

Component to load configuration from the database with caching:

```python
class DatabaseConfigProvider(ConfigProvider):
    """
    Configuration provider that loads requirements from the database.
    Includes caching for performance optimization.
    """
    
    def __init__(self, feature_flag_repository):
        self.repository = feature_flag_repository
        self._cache = {}
        self._cache_expiry = 0
        self._cache_ttl = 30  # Cache TTL in seconds
    
    async def get_repository_requirements(self):
        """Get repository method requirements with caching."""
        await self._refresh_cache_if_needed()
        return self._cache.get("repository", {})
        
    async def get_service_requirements(self):
        """Get service method requirements with caching."""
        await self._refresh_cache_if_needed()
        return self._cache.get("service", {})
        
    async def get_api_requirements(self):
        """Get API endpoint requirements with caching."""
        await self._refresh_cache_if_needed()
        return self._cache.get("api", {})
    
    async def _refresh_cache_if_needed(self):
        """Refresh the cache if it's expired."""
        current_time = time.time()
        if current_time > self._cache_expiry:
            await self._load_requirements()
            self._cache_expiry = current_time + self._cache_ttl
    
    async def _load_requirements(self):
        """Load all requirements from the database."""
        try:
            all_requirements = await self.repository.get_all_requirements()
            
            # Organize by layer
            repository_reqs = {}
            service_reqs = {}
            api_reqs = {}
            
            # Process requirements by type
            for flag_name, requirements in all_requirements.items():
                if "repository" in requirements:
                    repository_reqs[flag_name] = requirements["repository"]
                if "service" in requirements:
                    service_reqs[flag_name] = requirements["service"]
                if "api" in requirements:
                    api_reqs[flag_name] = requirements["api"]
            
            # Update cache
            self._cache = {
                "repository": repository_reqs,
                "service": service_reqs,
                "api": api_reqs
            }
        except Exception as e:
            logger.error(f"Error loading requirements: {e}")
            # Keep existing cache if available
            if not self._cache:
                self._cache = {"repository": {}, "service": {}, "api": {}}
```

4. **Repository Layer Interceptor**

The proxy pattern for repository layer enforcement:

```python
class FeatureFlagRepositoryProxy:
    """
    Proxy that wraps repository objects to enforce feature flag requirements.
    This provides a clean separation between repository logic and feature flag enforcement.
    """
    
    def __init__(self, repository, feature_flag_service, config_provider):
        self.repository = repository
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider
        
        # Log initialization for debugging
        self._log_initialization()
    
    def __getattr__(self, name):
        """
        Intercept attribute access to wrap methods with feature checking.
        Returns the original attribute for non-methods or methods without requirements.
        """
        original_attr = getattr(self.repository, name)
        
        # If not a method, return as-is
        if not callable(original_attr):
            return original_attr
            
        # Create a wrapped method with feature checking
        @functools.wraps(original_attr)
        async def wrapped_method(*args, **kwargs):
            # Get requirements for all flags
            requirements = await self.config_provider.get_repository_requirements()
            
            # Get the account type from args or kwargs
            account_type = None
            if args and len(args) > 0:
                account_type = args[0]
            elif 'account_type' in kwargs:
                account_type = kwargs['account_type']
            
            # Check if any flags have requirements for this method
            for flag_name, flag_requirements in requirements.items():
                if name in flag_requirements:
                    # Check if this account type is affected
                    if account_type and isinstance(flag_requirements[name], dict):
                        if account_type in flag_requirements[name]:
                            # Check if the flag is enabled
                            if not await self.feature_flag_service.is_enabled(flag_name):
                                # Raise domain-specific exception
                                raise FeatureDisabledError(
                                    flag_name, 
                                    entity_type="account_type", 
                                    entity_id=account_type
                                )
                    else:
                        # General method requirement
                        if not await self.feature_flag_service.is_enabled(flag_name):
                            raise FeatureDisabledError(flag_name, entity_type="method", entity_id=name)
            
            # If we get here, all required flags are enabled
            logger.debug(
                f"Feature flag check passed for {name}({account_type if account_type else ''})",
                extra={
                    "repository": self.repository.__class__.__name__,
                    "method": name,
                    "account_type": account_type
                }
            )
            return await original_attr(*args, **kwargs)
            
        return wrapped_method
        
    def _log_initialization(self):
        """Log proxy initialization for debugging."""
        logger.debug(
            f"FeatureFlagRepositoryProxy initialized for {self.repository.__class__.__name__}",
            extra={"repository": self.repository.__class__.__name__}
        )
```

5. **Domain-Specific Exceptions**

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

6. **Service Layer Interceptor** (Future Phase)

```python
class ServiceInterceptor:
    """
    Intercepts service method calls to enforce feature flag requirements.
    This separates service business logic from feature gating.
    """
    
    def __init__(self, feature_flag_service, config_provider):
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider
    
    async def intercept(self, service, method_name, args, kwargs):
        """
        Intercept service method calls to check feature flags.
        Raises FeatureDisabledError if a required feature is disabled.
        """
        # Get requirements for all flags
        requirements = await self.config_provider.get_service_requirements()
        
        # Check if any flags have requirements for this method
        for flag_name, flag_requirements in requirements.items():
            for pattern, methods in flag_requirements.items():
                if self._matches_pattern(method_name, pattern) and method_name in methods:
                    if not await self.feature_flag_service.is_enabled(flag_name):
                        raise FeatureDisabledError(flag_name, entity_type="service", entity_id=method_name)
                        
        # Log successful check
        logger.debug(
            f"Feature flag check passed for {method_name}",
            extra={
                "service": service.__class__.__name__,
                "method": method_name
            }
        )
        return True
        
    def _matches_pattern(self, method_name, pattern):
        """Check if a method name matches a pattern."""
        # Simple exact match
        if pattern == method_name:
            return True
            
        # Glob-style pattern matching
        return fnmatch.fnmatch(method_name, pattern)
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
        config_provider
    ):
        self.app = app
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider
        
    async def __call__(self, request, call_next):
        """ASGI middleware entry point."""
        # Get requirements for all flags
        requirements = await self.config_provider.get_api_requirements()
        
        # Check if any flags have requirements for this path
        for flag_name, flag_requirements in requirements.items():
            for pattern, paths in flag_requirements.items():
                if re.match(pattern, request.url.path):
                    if not await self.feature_flag_service.is_enabled(flag_name):
                        # Translate domain exception to HTTP response
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": f"Feature '{flag_name}' is not enabled",
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

### API Endpoints for Feature Flag Management

To support the frontend management interface (detailed in ADR-028), we will implement the following API endpoints:

#### Flag Values Management

```python
@router.get("/api/admin/feature-flags", response_model=List[FeatureFlagResponse])
async def get_feature_flags(
    feature_flag_repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all feature flags."""
    flags = await feature_flag_repository.get_all()
    return [
        FeatureFlagResponse(
            name=flag.name,
            value=flag.value,
            created_at=flag.created_at,
            updated_at=flag.updated_at
        ) for flag in flags
    ]

@router.get("/api/admin/feature-flags/{flag_name}", response_model=FeatureFlagDetailResponse)
async def get_feature_flag(
    flag_name: str,
    feature_flag_repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific feature flag."""
    flag = await feature_flag_repository.get_by_id(flag_name)
    if not flag:
        raise HTTPException(status_code=404, detail=f"Feature flag {flag_name} not found")
    
    return FeatureFlagDetailResponse(
        name=flag.name,
        value=flag.value,
        requirements=flag.requirements,
        created_at=flag.created_at,
        updated_at=flag.updated_at
    )

@router.put("/api/admin/feature-flags/{flag_name}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_name: str,
    flag_update: FeatureFlagUpdate,
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a feature flag value."""
    success = await feature_flag_service.set_enabled(flag_name, flag_update.value)
    if not success:
        raise HTTPException(status_code=404, detail=f"Feature flag {flag_name} not found")
    
    # Get updated flag
    flag = await feature_flag_service.get_flag(flag_name)
    return FeatureFlagResponse(
        name=flag.name,
        value=flag.value,
        created_at=flag.created_at,
        updated_at=flag.updated_at
    )
```

#### Requirements Management

```python
@router.get("/api/admin/feature-flags/{flag_name}/requirements", response_model=RequirementsResponse)
async def get_flag_requirements(
    flag_name: str,
    feature_flag_repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
    current_user: User = Depends(get_current_admin_user)
):
    """Get requirements for a specific feature flag."""
    try:
        requirements = await feature_flag_repository.get_requirements(flag_name)
        return RequirementsResponse(
            flag_name=flag_name,
            requirements=requirements
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/api/admin/feature-flags/{flag_name}/requirements", response_model=RequirementsResponse)
async def update_flag_requirements(
    flag_name: str,
    requirements: RequirementsUpdate,
    feature_flag_repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
    current_user: User = Depends(get_current_admin_user)
):
    """Update requirements for a specific feature flag."""
    try:
        updated_flag = await feature_flag_repository.update_requirements(
            flag_name, 
            requirements.requirements
        )
        return RequirementsResponse(
            flag_name=flag_name,
            requirements=updated_flag.requirements
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### History and Metrics

```python
@router.get("/api/admin/feature-flags/{flag_name}/history", response_model=List[FlagHistoryResponse])
async def get_flag_history(
    flag_name: str,
    feature_flag_repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
    current_user: User = Depends(get_current_admin_user)
):
    """Get history for a specific feature flag."""
    try:
        history = await feature_flag_repository.get_history(flag_name)
        return [
            FlagHistoryResponse(
                flag_name=flag_name,
                user=entry.user,
                timestamp=entry.timestamp,
                change_type=entry.change_type,
                old_value=entry.old_value,
                new_value=entry.new_value
            ) for entry in history
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/api/admin/feature-flags/{flag_name}/metrics", response_model=FlagMetricsResponse)
async def get_flag_metrics(
    flag_name: str,
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Get usage metrics for a specific feature flag."""
    try:
        metrics = await feature_flag_service.get_metrics(flag_name)
        return FlagMetricsResponse(
            flag_name=flag_name,
            check_count=metrics.check_count,
            layers={
                "repository": metrics.repository_count,
                "service": metrics.service_count,
                "api": metrics.api_count
            },
            last_checked=metrics.last_checked
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### Integration with Existing Codebase

#### Repository Factory Integration

```python
class RepositoryFactory:
    """Factory for creating repositories with specialized functionality."""
    
    @classmethod
    async def create_account_repository(
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
            # Create database-driven config provider
            config_provider = await cls._get_config_provider(session)
            return FeatureFlagRepositoryProxy(base_repo, feature_flag_service, config_provider)
            
        return base_repo
        
    @classmethod
    async def _get_config_provider(cls, session):
        """Get the database-driven configuration provider."""
        feature_flag_repository = FeatureFlagRepository(session)
        return DatabaseConfigProvider(feature_flag_repository)
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

# Requirements stored in database under BANKING_ACCOUNT_TYPES_ENABLED flag:
# {
#   "repository": {
#     "create_typed_account": {
#       "ewa": true,
#       "bnpl": true,
#       "payment_app": true
#     },
#     "update_typed_account": {
#       "ewa": true,
#       "bnpl": true,
#       "payment_app": true
#     },
#     "get_by_type": {
#       "ewa": true,
#       "bnpl": true,
#       "payment_app": true
#     }
#   },
#   "service": {
#     "create_account": true
#   },
#   "api": {
#     "/api/v1/accounts": true
#   }
# }
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
   - Flag values and requirements are cached in memory for performance
   - Cache has a short TTL (e.g., 30 seconds) to balance performance and freshness
   - Explicit cache invalidation on flag changes

### Implementation Plan

We will implement the feature flag system in a bottom-up approach, aligning with our current refactoring strategy:

1. **Phase 1: Repository Layer Implementation**
   - Update feature flag model with requirements column
   - Implement FeatureFlagError exception hierarchy
   - Create DatabaseConfigProvider
   - Implement FeatureFlagRepositoryProxy
   - Update RepositoryFactory to use the proxy
   - Seed initial requirements in the database
   - Fix affected tests

2. **Phase 2: Service Layer Implementation**
   - Build on foundation from Phase 1
   - Implement service interceptor pattern
   - Migrate service-layer feature flag checks to interceptor

3. **Phase 3: API Layer Implementation**
   - Add middleware for API-level feature flag enforcement
   - Create consistent HTTP responses for feature flag violations
   - Implement management API endpoints

### Default Feature Flags

The system will be initialized with the following feature flags and requirements:

1. `BANKING_ACCOUNT_TYPES_ENABLED`: Controls access to new banking account types (Payment App, BNPL, EWA)
   - Repository requirements: create_typed_account, update_typed_account, get_by_type for ewa, bnpl, payment_app
   - Service requirements: create_account, update_account for ewa, bnpl, payment_app
   - API requirements: /api/v1/accounts, /api/v1/accounts/*

2. `MULTI_CURRENCY_SUPPORT_ENABLED`: Controls support for multiple currencies in accounts
   - Repository requirements: create_account, update_account with currency fields
   - Service requirements: create_account, update_account with currency operations
   - API requirements: /api/v1/accounts with currency fields

3. `INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED`: Controls support for international banking fields (IBAN, SWIFT, etc.)
   - Repository requirements: create_account, update_account with international fields
   - Service requirements: create_account, update_account with international operations
   - API requirements: /api/v1/accounts with international fields

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
async def feature_flag_repository(db_session):
    """Create a feature flag repository for testing."""
    repository = FeatureFlagRepository(db_session)
    
    # Seed test requirements
    await repository.create({
        "name": "BANKING_ACCOUNT_TYPES_ENABLED",
        "value": True,
        "requirements": {
            "repository": {
                "create_typed_account": {
                    "ewa": True,
                    "bnpl": True,
                    "payment_app": True
                }
            }
        }
    })
    
    return repository

@pytest_asyncio.fixture
async def disabled_banking_types_feature_flag_service(feature_flag_service):
    """Feature flag service with banking types disabled."""
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    return feature_flag_service
```

## Frontend Management Interface

The frontend management interface for feature flags will be implemented as described in [ADR-028: Feature Flag Management Frontend](/code/debtonator/docs/adr/frontend/028-feature-flag-management-frontend.md). The backend API endpoints defined in this ADR will support the frontend requirements.

## Consequences

### Positive

1. **Clean Separation of Concerns**: Feature flag logic is centralized at architectural boundaries rather than scattered throughout the codebase
2. **Reduced Boilerplate**: Eliminates repetitive feature flag checking code in repositories and services
3. **Easier Maintenance**: Feature requirements are defined in one place for each layer
4. **Simpler Testing**: Tests can focus on business logic with clear feature flag configurations
5. **Consistent Enforcement**: Feature flags are enforced uniformly at each layer
6. **Runtime Configuration**: Both flag values and requirements can be updated at runtime without application restarts
7. **Database Consistency**: Using the database for both flag values and requirements ensures data consistency

### Negative

1. **Learning Curve**: Proxy and interceptor patterns may be less intuitive initially
2. **Debugging Complexity**: Issues might be harder to diagnose when enforcement happens in proxies
3. **Database Dependency**: Both flag values and requirements now depend on database availability
4. **Performance Considerations**: Database access for requirements may impact performance without proper caching

### Neutral

1. **Cache Management**: Need for proper cache invalidation and TTL settings
2. **Clear Boundaries Required**: Features must align well with architectural boundaries
3. **Documentation Need**: Requires clear documentation for future reference

## Performance Impact

The database-driven middleware/interceptor approach introduces additional performance considerations:

1. **Database Access**: Reading requirements from the database adds overhead
2. **Caching Mitigation**: Short-term caching (30-second TTL) mitigates most database overhead
3. **Proxy Wrapping**: Small overhead for method wrapping (typically microseconds)
4. **Pattern Matching**: Minor cost for URL and method pattern matching

With proper caching, the overall impact should remain under 1ms per request, which is negligible compared to database operations.

## Migration Strategy

Since we are only partially through implementing the original design, switching to the new approach has minimal migration cost:

1. **Database Schema Update**: Add requirements column to feature_flags table
2. **Repository Layer**: Implement proxy pattern and update tests
3. **Remove In-line Checks**: Gradually remove scattered feature flag checks
4. **Documentation**: Update memory bank with the new pattern
5. **Configuration**: Seed initial feature flag requirements in the database

## Success Metrics

We'll measure the success of the feature flag system by:

1. **Reduced Complexity**: Fewer lines of feature flag checking code throughout the codebase
2. **Test Simplification**: Cleaner integration tests for feature flag behavior
3. **Deployment Reliability**: Fewer incidents related to improperly enforced feature flags
4. **Code Quality**: Less duplication of feature flag checking logic
5. **Configuration Flexibility**: Ability to update requirements at runtime without code changes

## Related Documents

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-027: Dynamic Pay Period Rules](/code/debtonator/docs/adr/backend/027-dynamic-pay-period-rules.md)
- [ADR-028: Feature Flag Management Frontend](/code/debtonator/docs/adr/frontend/028-feature-flag-management-frontend.md)
