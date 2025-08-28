# 🔐 JWT Configuration

Django CFG provides comprehensive JWT authentication configuration through the `JWTConfig` class, offering type-safe, environment-aware JWT token management.

## Quick Start

```python
from django_cfg import DjangoConfig, JWTConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    
    # JWT Configuration
    jwt: JWTConfig = JWTConfig(
        access_token_lifetime_hours=24,
        refresh_token_lifetime_days=30,
    )

config = MyConfig()
```

## Configuration Options

### Token Lifetimes

```python
jwt: JWTConfig = JWTConfig(
    # Token lifetimes
    access_token_lifetime_hours=24,      # 1-8760 hours (1 year max)
    refresh_token_lifetime_days=30,      # 1-365 days (1 year max)
    
    # Token rotation
    rotate_refresh_tokens=True,          # Rotate tokens on refresh
    blacklist_after_rotation=True,       # Blacklist old tokens
)
```

### Security Settings

```python
jwt: JWTConfig = JWTConfig(
    # Security
    algorithm="HS256",                   # JWT signing algorithm
    update_last_login=True,              # Update user's last login
    leeway=0,                           # Token expiration leeway (seconds)
    
    # Optional claims
    audience="my-app",                   # JWT audience claim
    issuer="my-company",                 # JWT issuer claim
)
```

### Token Claims

```python
jwt: JWTConfig = JWTConfig(
    # Claims configuration
    user_id_field="id",                  # User model field for ID
    user_id_claim="user_id",             # JWT claim name for user ID
    token_type_claim="token_type",       # JWT claim name for token type
    jti_claim="jti",                     # JWT claim name for token ID
)
```

### Authentication Headers

```python
jwt: JWTConfig = JWTConfig(
    # Header configuration
    auth_header_types=("Bearer",),       # Accepted header types
    auth_header_name="HTTP_AUTHORIZATION", # HTTP header name
)
```

## Environment-Aware Configuration

JWT configuration automatically adapts to different environments:

### Development Environment
```python
# Automatically configured for development
jwt_dev = jwt_config.configure_for_environment("development", debug=True)
# Result: 1 hour access, 7 days refresh, 30s leeway
```

### Production Environment
```python
# Automatically configured for production
jwt_prod = jwt_config.configure_for_environment("production", debug=False)
# Result: 24 hours access, 30 days refresh, 0s leeway
```

### Testing Environment
```python
# Automatically configured for testing
jwt_test = jwt_config.configure_for_environment("testing")
# Result: 1 hour access, 1 day refresh, no rotation
```

## Advanced Usage

### Custom Environment Configuration

```python
class MyConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig()
    
    def __post_init__(self):
        # Configure JWT based on environment
        if self.debug:
            # Development: short-lived tokens
            self.jwt = self.jwt.configure_for_environment("development", True)
        else:
            # Production: long-lived tokens
            self.jwt = self.jwt.configure_for_environment("production", False)
```

### Token Information

```python
# Get human-readable token info
token_info = config.jwt.get_token_info()
print(token_info)
# Output: {
#     'access_token': '24 hours',
#     'refresh_token': '30 days', 
#     'algorithm': 'HS256',
#     'rotation': 'enabled'
# }
```

### Manual Django Settings

If you need to access the raw Django settings:

```python
# Get Django SIMPLE_JWT settings
jwt_settings = config.jwt.to_django_settings(config.secret_key)
print(jwt_settings['SIMPLE_JWT']['ACCESS_TOKEN_LIFETIME'])
# Output: datetime.timedelta(hours=24)
```

## Supported Algorithms

- **HMAC**: HS256, HS384, HS512
- **RSA**: RS256, RS384, RS512  
- **ECDSA**: ES256, ES384, ES512

## Integration with Django REST Framework

The JWT configuration automatically integrates with `djangorestframework-simplejwt`:

```python
# In your DRF views
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    # Automatically uses your JWT configuration
    pass
```

## Best Practices

### 1. Environment-Specific Lifetimes
```python
class MyConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        # Short tokens for development
        access_token_lifetime_hours=1 if debug else 24,
        refresh_token_lifetime_days=7 if debug else 30,
    )
```

### 2. Security in Production
```python
class ProductionConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        algorithm="RS256",              # Use RSA for production
        leeway=0,                       # No leeway in production
        rotate_refresh_tokens=True,     # Always rotate tokens
        blacklist_after_rotation=True, # Blacklist old tokens
    )
```

### 3. Testing Configuration
```python
class TestConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        access_token_lifetime_hours=1,
        refresh_token_lifetime_days=1,
        rotate_refresh_tokens=False,    # Simpler for tests
        blacklist_after_rotation=False,
    )
```

## Troubleshooting

### Token Expiration Issues
```python
# Check current token lifetimes
print(f"Access token: {config.jwt.access_token_lifetime_hours} hours")
print(f"Refresh token: {config.jwt.refresh_token_lifetime_days} days")
```

### Algorithm Validation Errors
```python
# Ensure you're using a supported algorithm
try:
    jwt_config = JWTConfig(algorithm="INVALID")
except ValueError as e:
    print(f"Invalid algorithm: {e}")
```

### Environment Detection
```python
# Verify environment configuration
env_jwt = config.jwt.configure_for_environment("production")
print(f"Production access token: {env_jwt.access_token_lifetime_hours} hours")
```

## Migration from Manual Configuration

### Before (Manual SIMPLE_JWT)
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    # ... many more settings
}
```

### After (Django CFG)
```python
# config.py
class MyConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        access_token_lifetime_hours=24,
        refresh_token_lifetime_days=30,
    )
    # All other settings are automatically configured!
```

## Related Documentation

- [Django REST Framework Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT token debugger
- [Django CFG Core Configuration](./core-configuration.md)
