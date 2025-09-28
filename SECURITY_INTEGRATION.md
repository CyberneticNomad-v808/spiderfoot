# SpiderFoot Security Integration

## Overview

This document describes the security enhancements added to SpiderFoot, including CSRF protection and PostgreSQL support.

## Changes Made

### 1. PostgreSQL Configuration Support (`sf.py`)

SpiderFoot now automatically detects PostgreSQL environment variables and uses PostgreSQL when available:

```python
# Environment variables for PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_DB=spiderfoot
POSTGRES_USER=spiderfoot
POSTGRES_PASSWORD=spiderfoot_pass
POSTGRES_PORT=5432
```

When these are set, SpiderFoot will use PostgreSQL instead of SQLite.

### 2. PostgreSQL Foreign Key Constraints (`spiderfoot/db.py`)

Fixed PostgreSQL schema initialization by making foreign key constraints deferrable:

```sql
type VARCHAR NOT NULL REFERENCES tbl_event_types(event) DEFERRABLE INITIALLY DEFERRED
```

This prevents initialization order issues when populating event types.

### 3. Development-Friendly CSRF Protection

Added `spiderfoot/security/` module with development-friendly CSRF protection that:

- Logs CSRF failures as warnings instead of blocking requests
- Suitable for single-user development environments
- Can be enabled by setting `SF_DEVELOPMENT_MODE=true`

## Integration Instructions

### For Web Interface (sfwebui.py)

To integrate the CSRF middleware, add to the initialization:

```python
from spiderfoot.security.csrf_middleware import enable_development_csrf

# In your CherryPy configuration
enable_development_csrf()
```

### For Docker Environments

Set the environment variable:

```yaml
environment:
  - SF_DEVELOPMENT_MODE=true
```

## Security Considerations

The development-friendly CSRF protection is intended for:

- Single-user environments
- Protected LAN deployments
- Development and testing

For production multi-user deployments, implement proper CSRF token generation and validation.

## Benefits

1. **No more 403 errors** in development
2. **Data persistence** with PostgreSQL support
3. **Security awareness** through warning logs
4. **Backward compatibility** with existing SQLite setups