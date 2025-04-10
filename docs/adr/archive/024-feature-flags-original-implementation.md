# ADR-024: Feature Flag System

## Status

Proposed

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
6. Standardized approach to feature integration throughout the codebase

### Feature Flag Types

The system will support the following types of feature flags:

1. **Boolean Flags**: Simple on/off toggles for features across the entire application
2. **Percentage Rollout Flags**: Gradual rollout to a percentage of users
3. **User Segment Flags**: Enable features for specific user segments based on criteria (e.g., admin users, beta testers)
4. **Time-Based Flags**: Automatically enable/disable features based on schedule

### Technical Implementation

#### Core Components

1. **Feature Flag Registry**

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
        
        # For simple boolean flags, just return the value
        if flag["type"] == "boolean":
            return flag["value"]
        
        # For percentage rollout, use the context (e.g., user ID) to determine
        if flag["type"] == "percentage" and context and "user_id" in context:
            percentage = flag["value"]
            user_id = context["user_id"]
            # Use a hash of the flag name and user ID to get consistent behavior
            return self._is_user_in_percentage(user_id, flag_name, percentage)
        
        # For user segment flags, check if user is in the segment
        if flag["type"] == "user_segment" and context and "user" in context:
            segments = flag["value"]
            user = context["user"]
            return self._is_user_in_segment(user, segments)
        
        # For time-based flags, check if current time is within the specified range
        if flag["type"] == "time_based":
            start_time = flag["metadata"].get("start_time")
            end_time = flag["metadata"].get("end_time")
            now = datetime.now(timezone.utc)
            if start_time and now < start_time:
                return False
            if end_time and now > end_time:
                return False
            return True
        
        # Default fallback
        return flag["value"]
    
    def set_value(self, flag_name, value):
        """Set the value of a feature flag."""
        if flag_name not in self._flags:
            raise ValueError(f"Unknown feature flag: {flag_name}")
        
        old_value = self._flags[flag_name]["value"]
        self._flags[flag_name]["value"] = value
        
        # Notify observers if value changed
        if old_value != value:
            for observer in self._observers:
                observer.flag_changed(flag_name, old_value, value)
    
    def get_all_flags(self):
        """Get all registered feature flags and their current values."""
        return {name: flag.copy() for name, flag in self._flags.items()}
    
    def add_observer(self, observer):
        """Add an observer to be notified when flag values change."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _is_user_in_percentage(self, user_id, flag_name, percentage):
        """Determine if a user falls within the percentage rollout."""
        # Create a hash from user_id and flag_name to ensure consistent behavior
        hash_input = f"{user_id}:{flag_name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        # Normalize to 0-100 range
        bucket = hash_value % 100
        return bucket < percentage
    
    def _is_user_in_segment(self, user, segments):
        """Determine if a user is in any of the specified segments."""
        for segment in segments:
            if segment == "admin" and user.is_admin:
                return True
            if segment == "beta" and user.is_beta_tester:
                return True
            # Add more segment checks as needed
        return False
```

2. **Feature Flag Storage**

```python
class FeatureFlagStorage:
    """Interface for feature flag persistence."""
    
    def load_flags(self):
        """Load feature flag values from storage."""
        raise NotImplementedError()
    
    def save_flag(self, flag_name, value):
        """Save a feature flag value to storage."""
        raise NotImplementedError()
    
    def save_all_flags(self, flags):
        """Save all feature flag values to storage."""
        raise NotImplementedError()

class DatabaseFeatureFlagStorage(FeatureFlagStorage):
    """Database implementation of feature flag storage."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def load_flags(self):
        """Load feature flags from database."""
        session = self.session_factory()
        try:
            flag_records = session.query(FeatureFlag).all()
            return {record.name: record.value for record in flag_records}
        finally:
            session.close()
    
    def save_flag(self, flag_name, value):
        """Save a feature flag value to database."""
        session = self.session_factory()
        try:
            flag = session.query(FeatureFlag).filter_by(name=flag_name).first()
            if flag:
                flag.value = value
            else:
                flag = FeatureFlag(name=flag_name, value=value)
                session.add(flag)
            session.commit()
        finally:
            session.close()
    
    def save_all_flags(self, flags):
        """Save all feature flag values to database."""
        session = self.session_factory()
        try:
            for name, value in flags.items():
                flag = session.query(FeatureFlag).filter_by(name=name).first()
                if flag:
                    flag.value = value
                else:
                    flag = FeatureFlag(name=name, value=value)
                    session.add(flag)
            session.commit()
        finally:
            session.close()
```

3. **Feature Flag Service**

```python
class FeatureFlagService:
    """Service for managing feature flags."""
    
    def __init__(self, registry, storage):
        self.registry = registry
        self.storage = storage
        self._initialize()
    
    def _initialize(self):
        """Initialize the registry from storage."""
        stored_values = self.storage.load_flags()
        
        # Update registry with stored values
        for flag_name, value in stored_values.items():
            if flag_name in self.registry._flags:
                self.registry._flags[flag_name]["value"] = value
    
    def is_enabled(self, flag_name, context=None):
        """Check if a feature flag is enabled."""
        try:
            value = self.registry.get_value(flag_name, context)
            # For boolean flags, the value is the enabled state
            # For percentage/segment flags, the result of evaluation is the enabled state
            return bool(value)
        except ValueError:
            # If flag doesn't exist, default to disabled
            return False
    
    def set_enabled(self, flag_name, enabled, persist=True):
        """Enable or disable a feature flag."""
        try:
            # Update the registry
            self.registry.set_value(flag_name, enabled)
            
            # Persist the change if requested
            if persist:
                self.storage.save_flag(flag_name, enabled)
                
            return True
        except ValueError:
            return False
    
    def get_all_flags(self):
        """Get all registered feature flags and their current values."""
        return self.registry.get_all_flags()
```

4. **Flag Configuration Integration**

```python
def configure_feature_flags(app):
    """Configure feature flags for the application."""
    # Create the registry
    registry = FeatureFlagRegistry()
    
    # Register all feature flags with default values
    registry.register(
        "BANKING_ACCOUNT_TYPES_ENABLED", 
        "boolean", 
        False, 
        "Enable new banking account types from ADR-019"
    )
    
    registry.register(
        "MULTI_CURRENCY_SUPPORT_ENABLED", 
        "boolean", 
        False, 
        "Enable multi-currency support for accounts"
    )
    
    registry.register(
        "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED", 
        "boolean", 
        False, 
        "Enable international account support (IBAN, SWIFT, etc.)"
    )
    
    # Add more feature flags as needed...
    
    # Create storage
    storage = DatabaseFeatureFlagStorage(app.session_factory)
    
    # Create service
    service = FeatureFlagService(registry, storage)
    
    # Add to application context
    app.feature_flag_service = service
    
    return service
```

5. **Database Model**

```python
class FeatureFlag(Base):
    """Database model for feature flags."""
    
    __tablename__ = "feature_flags"
    
    name = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<FeatureFlag name={self.name} value={self.value}>"
```

### Integration with Existing Codebase

#### Integration with FastAPI Dependency Injection

```python
def get_feature_flag_service():
    """Dependency provider for feature flag service."""
    return app.feature_flag_service

@router.get("/api/feature-flags", response_model=List[FeatureFlagResponse])
def get_feature_flags(
    current_user: User = Depends(get_current_user),
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Get all feature flags and their status."""
    # Only admins can view feature flags
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    flags = feature_flag_service.get_all_flags()
    return [
        FeatureFlagResponse(
            name=name,
            type=flag["type"],
            value=flag["value"],
            description=flag["description"]
        )
        for name, flag in flags.items()
    ]

@router.post("/api/feature-flags/{flag_name}/toggle", response_model=FeatureFlagResponse)
def toggle_feature_flag(
    flag_name: str,
    value: bool,
    current_user: User = Depends(get_current_user),
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Toggle a feature flag."""
    # Only admins can toggle feature flags
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = feature_flag_service.set_enabled(flag_name, value)
    if not success:
        raise HTTPException(status_code=404, detail=f"Feature flag {flag_name} not found")
    
    flag = feature_flag_service.get_all_flags()[flag_name]
    return FeatureFlagResponse(
        name=flag_name,
        type=flag["type"],
        value=flag["value"],
        description=flag["description"]
    )
```

#### Integration in Repository Layer

```python
class AccountRepository(BaseRepository):
    """Repository for account entities."""
    
    def __init__(self, session, feature_flag_service):
        super().__init__(session)
        self.feature_flag_service = feature_flag_service
        self.model_class = Account
    
    def get_account_types(self):
        """Get all available account types."""
        # Base account types always available
        account_types = ["checking", "savings", "credit"]
        
        # Add new banking account types if enabled
        if self.feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
            account_types.extend(["payment_app", "bnpl", "ewa"])
        
        return account_types
    
    def create_account(self, data):
        """Create a new account."""
        account_type = data.get("account_type")
        
        # Validate account type based on feature flags
        if account_type not in self.get_account_types():
            raise ValueError(f"Account type {account_type} is not available")
        
        # Check for multi-currency support
        if "currency" in data and not self.feature_flag_service.is_enabled("MULTI_CURRENCY_SUPPORT_ENABLED"):
            raise ValueError("Multi-currency support is not enabled")
        
        # Check for international account fields
        international_fields = ["iban", "swift_bic", "sort_code", "branch_code"]
        has_international_fields = any(field in data for field in international_fields)
        
        if has_international_fields and not self.feature_flag_service.is_enabled("INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED"):
            raise ValueError("International account support is not enabled")
        
        # Proceed with account creation
        return super().create(data)
```

#### Integration in Service Layer

```python
class AccountService:
    """Service for account operations."""
    
    def __init__(self, account_repository, feature_flag_service):
        self.account_repository = account_repository
        self.feature_flag_service = feature_flag_service
    
    def create_account(self, data):
        """Create a new account."""
        # Clean data based on feature flags
        cleaned_data = self._clean_data_based_on_flags(data)
        
        # Create the account
        return self.account_repository.create_account(cleaned_data)
    
    def _clean_data_based_on_flags(self, data):
        """Remove fields that aren't enabled by feature flags."""
        cleaned_data = data.copy()
        
        # Remove currency if multi-currency not enabled
        if "currency" in cleaned_data and not self.feature_flag_service.is_enabled("MULTI_CURRENCY_SUPPORT_ENABLED"):
            del cleaned_data["currency"]
        
        # Remove international fields if not enabled
        if not self.feature_flag_service.is_enabled("INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED"):
            for field in ["iban", "swift_bic", "sort_code", "branch_code"]:
                if field in cleaned_data:
                    del cleaned_data[field]
        
        return cleaned_data
```

#### Integration in API Layer

```python
@router.post("/accounts", response_model=AccountResponse)
def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Create a new account."""
    # Check if the account type is enabled
    account_type = account_data.account_type
    
    if account_type in ["payment_app", "bnpl", "ewa"] and not feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
        raise HTTPException(
            status_code=400,
            detail=f"Account type {account_type} is not currently available"
        )
    
    # Add user_id to data
    data_dict = account_data.model_dump()
    data_dict["user_id"] = current_user.id
    
    # Create the account
    return account_service.create_account(data_dict)
```

### Admin Interface

We will implement an admin dashboard for managing feature flags with the following capabilities:

1. View all feature flags and their current status
2. Toggle boolean flags on/off
3. Configure percentage rollout flags
4. Configure user segment flags
5. View flag change history
6. Configure time-based flags

The admin interface will be restricted to users with administrative privileges.

### Feature Flag Monitoring

To properly track feature flag usage and changes, we will implement:

1. Logging of all feature flag changes (who changed it, when, old value, new value)
2. Metrics tracking how often each flag is checked
3. Alerts for flags that have been in a "temporary" state for too long
4. Dashboard for visualizing feature flag status across environments

### Default Feature Flags

The system will be initialized with the following feature flags:

1. `BANKING_ACCOUNT_TYPES_ENABLED`: Controls access to new banking account types (Payment App, BNPL, EWA)
2. `MULTI_CURRENCY_SUPPORT_ENABLED`: Controls support for multiple currencies in accounts
3. `INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED`: Controls support for international banking fields (IBAN, SWIFT, etc.)

These flags will default to `false` in all environments except development, where they may be enabled for testing purposes.

## Consequences

### Positive

1. **Controlled Deployments**: Features can be deployed but remain disabled until ready for release
2. **Gradual Rollout**: New features can be rolled out to small segments of users first to identify issues
3. **Quick Response to Problems**: Problematic features can be immediately disabled without code rollback
4. **Testing in Production**: Features can be tested in the production environment with limited exposure
5. **Flexible Release Management**: Different features can be released on independent timelines
6. **Better Debugging**: Feature flags can aid in troubleshooting by isolating different features
7. **User Segmentation**: Features can be enabled for specific user groups (e.g., beta testers, admins)

### Negative

1. **Increased Complexity**: Code paths must handle both enabled and disabled states for features
2. **Technical Debt**: Old feature flags must be removed after features are fully deployed
3. **Testing Overhead**: Each feature must be tested in both enabled and disabled states
4. **Potential for Inconsistency**: If not managed carefully, users might experience inconsistent behavior
5. **Database Dependency**: Feature flag state relies on database, adding a potential point of failure

### Neutral

1. **Configuration Management**: Feature flag states must be tracked across environments
2. **Developer Education**: Team must learn to properly integrate with the feature flag system
3. **UI Adaptation**: Frontend must adapt to handle features that may or may not be available

## Performance Impact

The feature flag system introduces minimal performance overhead:

1. **Database Reads**: Flag values are loaded at application startup and cached in memory
2. **Flag Checks**: Each flag check is an in-memory operation (O(1) time complexity)
3. **Database Writes**: Only occur when flag values are changed (infrequent operation)

We expect the system to add less than 1ms overhead per request, which is negligible compared to typical database operations.

## Implementation Plan

1. **Phase 1: Core Infrastructure** (Week 1)
   - Implement FeatureFlagRegistry
   - Implement FeatureFlagStorage
   - Implement FeatureFlagService
   - Create database model and migration
   - Implement basic API endpoints for flags

2. **Phase 2: Integration** (Week 2)
   - Update dependency injection system
   - Integrate with repository layer
   - Integrate with service layer
   - Integrate with API layer
   - Implement feature flag middleware

3. **Phase 3: Admin Interface** (Week 3)
   - Create admin dashboard for flag management
   - Implement flag history tracking
   - Create visualization for flag status
   - Implement user segment management

4. **Phase 4: Monitoring and Rollout** (Week 4)
   - Implement monitoring and metrics
   - Create dashboards for flag usage
   - Develop rollout strategy for each flag
   - Train team on feature flag usage

## Migration Strategy

The feature flag system will be implemented before enabling the new account types from ADR-019. This ensures that we have a controlled mechanism for rolling out these new features.

Once the feature flag system is in place, we'll update the existing implementation checklists for ADR-016 and ADR-019 to include integration with feature flags at each layer of the application.

## Success Metrics

We'll measure the success of the feature flag system by:

1. **Deployment Speed**: Time from code complete to first production exposure should decrease
2. **Incident Response Time**: Time to disable problematic features should be under 5 minutes
3. **Rollback Frequency**: We should see fewer full rollbacks as issues can be isolated
4. **Feature Adoption Rate**: We can measure adoption as we gradually roll out features
5. **Developer Satisfaction**: Surveyed confidence in deploying new features should increase

## Related Documents

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-016 Implementation Checklist](/code/debtonator/docs/adr/implementation/adr016-implementation-checklist.md)
- [ADR-019 Implementation Checklist](/code/debtonator/docs/adr/implementation/adr019-implementation-checklist.md)
