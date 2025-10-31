# REAL DATABASE PERSISTENCE BUGS

**Date:** 2025-10-30
**Severity:** CRITICAL
**Status:** Confirmed via manual testing

## Summary

The regression tests in `test/regression/test_database_settings_persistence.py` are BOGUS because they mock away the actual production code paths. In reality, Spiderfoot has THREE critical database bugs that cause data loss on every container restart.

## Bug #1: Environment Variables Never Read

**File:** `sf.py`
**Line:** ~100 (sfConfig initialization)

**Problem:**
```python
sfConfig = {
    '__database': '',  # ← EMPTY! Never reads environment variables
    # ...
}
```

**Expected Behavior:**
Should read `SPIDERFOOT_DB_HOST`, `SPIDERFOOT_DB_PORT`, `SPIDERFOOT_DB` from environment and construct PostgreSQL connection string.

**Actual Behavior:**
Environment variables are completely ignored. Config always starts with empty database string.

**Evidence from Production:**
```bash
$ docker exec number-two-scope env | grep SPIDERFOOT_DB
SPIDERFOOT_DB_HOST=unified-postgres
SPIDERFOOT_DB_PORT=5432
SPIDERFOOT_DB=spiderfoot_db

$ docker exec unified-postgres psql -U postgres -d spiderfoot_db -c "\dt"
Did not find any relations.  # ← DATABASE IS EMPTY!

$ docker exec number-two-scope ls -lh /home/spiderfoot/data/spiderfoot.db
-rw-r--r-- 1 root 1000 124K Oct 30 21:15 /home/spiderfoot/data/spiderfoot.db
# ← SQLite being used instead!
```

## Bug #2: Hardcoded SQLite Fallback in WebUI

**File:** `spiderfoot/webui/routes.py`
**Line:** 1097

**Problem:**
```python
# Validate database configuration
if '__database' not in self.config:
    self.config['__database'] = 'spiderfoot.db'  # ← HARDCODED!
```

**Actual Behavior:**
Even if environment variables WERE read, this code would override them with SQLite.

## Bug #3: Settings Saved to Wrong Database

**File:** Multiple (WebUI settings endpoints)

**Problem:**
When a user changes database settings in the WebUI:
1. Settings are saved to SQLite (`/home/spiderfoot/data/spiderfoot.db`)
2. Application continues using SQLite
3. PostgreSQL remains empty
4. On restart, SQLite is recreated/lost

**Evidence from Production:**
```bash
$ docker exec number-two-scope python3 -c "
from spiderfoot import SpiderFootDb
dbh = SpiderFootDb({'__database': '/home/spiderfoot/data/spiderfoot.db'}, init=False)
config = dbh.configGet()
for key, value in config.items():
    if 'stor_db' in key and 'postgresql' in key:
        print(f'{key} = {value}')
"

sfp__stor_db:postgresql_host = localhost  # ← WRONG! Should be unified-postgres
sfp__stor_db:postgresql_database = spiderfoot  # ← WRONG! Should be spiderfoot_db
sfp__stor_db:db_type = postgresql  # ← Says PostgreSQL but using SQLite!
```

The settings ARE persisted to SQLite, but:
- They have wrong values (localhost vs unified-postgres)
- They're never actually used
- PostgreSQL is never initialized
- SQLite gets lost on container restart

## Why The Regression Tests Are Bogus

**File:** `test/regression/test_database_settings_persistence.py`

**Problem:**
All tests use temporary in-memory SQLite databases:
```python
self.test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
```

The tests NEVER:
1. Check if environment variables are read
2. Test PostgreSQL connection
3. Verify settings persist across container restarts
4. Test the actual production code path in `sf.py`

The tests validate that the serialization/deserialization logic works, but completely miss that:
- Environment variables are never read
- Default config is hardcoded to SQLite
- PostgreSQL is never initialized

## Impact

**User-Visible Symptoms:**
1. Save database settings in WebUI → Settings not applied
2. Create workspace/scan → Lost on container restart
3. Configure PostgreSQL → Still using SQLite
4. Container restart → All data gone

**Data Loss Scenario:**
1. User creates 10 workspaces with scan data
2. Settings show PostgreSQL configured
3. Container restarts (system update, crash, deploy)
4. ALL workspaces and scans are GONE
5. User has to re-create everything

## Root Cause

The fundamental issue is that Spiderfoot was designed for standalone SQLite usage, and PostgreSQL support was added later without proper integration with:
1. Container environment variables
2. Production deployment patterns
3. WebUI initialization flow

## Required Fixes

### Fix #1: Read Environment Variables in sf.py

```python
# In sf.py, before sfConfig definition
import os

# Read database config from environment
DB_TYPE = os.getenv('SPIDERFOOT_DB_TYPE', 'sqlite')
if DB_TYPE == 'postgresql':
    DB_HOST = os.getenv('SPIDERFOOT_DB_HOST', 'localhost')
    DB_PORT = os.getenv('SPIDERFOOT_DB_PORT', '5432')
    DB_NAME = os.getenv('SPIDERFOOT_DB', 'spiderfoot')
    DB_USER = os.getenv('SPIDERFOOT_DB_USER', 'spiderfoot')
    DB_PASS = os.getenv('SPIDERFOOT_DB_PASSWORD', '')

    # Construct PostgreSQL connection string
    sfConfig['__database'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Default to SQLite
    sfConfig['__database'] = f"{SpiderFootHelpers.dataPath()}/spiderfoot.db"
```

### Fix #2: Remove Hardcoded SQLite Fallback

```python
# In spiderfoot/webui/routes.py, line 1096-1097
# REMOVE THIS:
# if '__database' not in self.config:
#     self.config['__database'] = 'spiderfoot.db'

# REPLACE WITH:
if '__database' not in self.config or not self.config['__database']:
    raise ValueError("Database configuration is required but not set")
```

### Fix #3: Initialize PostgreSQL Database

Need to ensure PostgreSQL database is initialized with proper schema on first startup.

### Fix #4: Add REAL Regression Tests

```python
def test_environment_variables_are_read():
    """Verify that SPIDERFOOT_DB_* environment variables are actually used."""
    os.environ['SPIDERFOOT_DB_HOST'] = 'testhost'
    os.environ['SPIDERFOOT_DB_PORT'] = '5433'
    os.environ['SPIDERFOOT_DB'] = 'testdb'

    # Import sf.py (which should read env vars)
    import sf

    # Verify database config was set from env vars
    assert 'testhost' in sf.sfConfig['__database']
    assert '5433' in sf.sfConfig['__database']
    assert 'testdb' in sf.sfConfig['__database']
```

## Verification Steps

After fixes are applied:

1. **Verify environment variables are read:**
```bash
docker exec number-two-scope python3 -c "
from sf import sfConfig
print('Database config:', sfConfig['__database'])
"
# Should print PostgreSQL connection string, not SQLite path
```

2. **Verify PostgreSQL is used:**
```bash
docker exec unified-postgres psql -U postgres -d spiderfoot_db -c "\dt"
# Should show tables, not "Did not find any relations"
```

3. **Verify settings persist:**
```bash
# 1. Change a setting in WebUI
# 2. Restart container: docker restart number-two-scope
# 3. Check setting is still there
```

4. **Verify scans persist:**
```bash
# 1. Create a scan
# 2. Restart container
# 3. Verify scan still exists
```

## Timeline

- **Oct 29 2025:** Regression tests written (but they test the wrong thing)
- **Oct 30 2025:** User reports settings don't persist
- **Oct 30 2025:** Investigation reveals environment variables never read
- **Oct 30 2025:** Confirmed PostgreSQL database is completely empty

## Related Files

- `sf.py` - Main entry point (needs env var reading)
- `spiderfoot/webui/routes.py` - WebUI initialization (needs hardcode removal)
- `sfwebui.py` - WebUI wrapper (needs validation fixes)
- `test/regression/test_database_settings_persistence.py` - Tests (need to test real code paths)
- `docker-compose.yml` - Sets env vars (but they're ignored)

## Conclusion

The regression tests give FALSE CONFIDENCE that database persistence works, when in reality:
1. Environment variables are never read
2. PostgreSQL is never used
3. All data is lost on restart
4. Settings changes have no effect

This is a CRITICAL production bug causing data loss.
