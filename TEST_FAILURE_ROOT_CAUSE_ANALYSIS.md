# SpiderFoot Test Failure Root Cause Analysis
**Date:** February 14, 2026
**Test Run:** February 12, 2026 02:11:40
**Results:** 323 failed, 2,254 passed, 288 skipped, 19 warnings, 85 errors

## Executive Summary

Test failures stem from 5 primary root causes, with the most critical being the PostgreSQL/SQLite configuration mismatch that accounts for ~140 failures/errors. The issues are systemic and affect database layer, configuration management, and external API integration.

---

## Root Cause #1: SQLite Removal Incomplete (CRITICAL)
**Impact:** 85 ERRORs + ~50 failures (~140 total)
**Priority:** HIGHEST

### Problem
The database layer (`spiderfoot/db/db_core.py:744`) now rejects SQLite paths but:
- Tests still attempt to use SQLite (`:memory:`, `/tmp/*.db`)
- Code doesn't properly detect backend type
- No migration path for temporary test storage

### Evidence
```
ValueError: Invalid PostgreSQL connection string: ':memory:'
Expected DSN URI format: postgresql://user:password@host:port/database

ValueError: Invalid PostgreSQL connection string: '/tmp/spiderfoot_test_9uqjn8y9/spiderfoot_test.db'
```

### Affected Components
- `spiderfoot/db/db_core.py` - Connection string validation
- `test/conftest.py` - Default test configuration
- All integration tests expecting in-memory DB
- `test_spiderfootscanner.py` - All 35+ tests
- `test_correlation_engine_integration.py` - All 12 tests
- `test_sfwebui.py` - All 45+ tests

### Required Actions
1. **Remove all SQLite code paths** from:
   - `spiderfoot/db/db_core.py`
   - `spiderfoot/db/__init__.py`
   - `modules/sfp__stor_db.py`
   
2. **Replace SQLite usage** with:
   - PostgreSQL for persistent test data
   - Redis (`unified-redis`) for temporary/ephemeral storage
   
3. **Update test fixtures** to use PostgreSQL with proper isolation:
   - Transaction rollback per test
   - Separate schemas per test class
   - Database cleanup fixtures

4. **Fix configuration precedence**:
   - Environment variables should not leak into tests
   - Test config should override global config
   - Add `pytest.ini` or fixture to set `SPIDERFOOT_DB_*` vars correctly

---

## Root Cause #2: Module Options Schema Mismatch
**Impact:** 45 "test_opts FAILED"
**Priority:** HIGH

### Problem
Module `opts` dictionary contains global/inherited options (14 keys) but `optdescs` only has module-specific descriptions (3 keys). Tests expect 1:1 mapping.

### Evidence
```python
AssertionError: 14 != 3  # len(module.opts) != len(module.optdescs)
```

### Architectural Issue
Global configuration options are being merged into module-level `opts`, likely from recent configuration system refactor. This breaks the contract that every opt has a description.

### Affected Modules (45+)
- abstractapi, abuseipdb, accounts, adblock, adguard_dns, ahmia, alienvault
- arin, azureblobstorage, bambenek, bingsearch, blockchain, botscout, botvrij
- builtwith, c99, callername, censys, certspotter, cinsscore, circllu, citadel
- cleanbrowsing, cloudflaredns, and 20+ more

### Required Actions
1. **Investigate configuration merge** in:
   - Module loading code
   - Configuration initialization
   - SpiderFootPlugin base class
   
2. **Choose architecture**:
   - **Option A:** Filter global opts from module opts
   - **Option B:** Add global optdescs to all modules
   - **Option C:** Separate global_opts from module_opts
   
3. **Fix tests** or **fix implementation** based on chosen architecture

4. **Document** the intended behavior of opts/optdescs relationship

---

## Root Cause #3: Storage Module PostgreSQL-Only Configuration
**Impact:** 5 failures in `test_sfp__stor_db.py`
**Priority:** HIGH

### Problem
Storage module (`sfp__stor_db`) attempts PostgreSQL connection even when tests configure SQLite, because environment variables override test config.

### Evidence
```
ERROR: Could not connect to PostgreSQL database: 
connection to server at "unified-postgres.blk.ing" (192.168.169.5), 
port 5432 failed: FATAL: password authentication failed for user "spiderfoot"
```

### Root Issue
- `conftest.py` lines 13-17 set global env vars
- These leak into all tests
- Module reads `os.environ` at class definition time
- Test isolation is broken

### Required Actions
1. **Fix test isolation**:
   - Move env var setup to fixtures (not global)
   - Use `monkeypatch` fixture to set env vars per-test
   - Clear DB env vars in teardown

2. **Fix module env reading**:
   - Don't read `os.environ` at class level
   - Read in `__init__` or `setup()` methods
   - Accept explicit config overrides

3. **Update storage tests**:
   - Mock PostgreSQL connections
   - Use test database transactions
   - Add rollback fixtures

---

## Root Cause #4: URL Validation Null Handling Bug
**Impact:** 2 failures in `test_spiderfoot.py`
**Priority:** MEDIUM

### Problem
`urlFQDN()` returns `None` for invalid URLs instead of empty string or exception. Calling code doesn't check for None before calling `.lower()`.

### Evidence
```python
spiderfoot/sflib/network.py:187: host = urlFQDN(url).lower()
AttributeError: 'NoneType' object has no attribute 'lower'
```

### Stack Trace
```
test_fetchUrl_argument_url_invalid_type_should_return_none
test_fetchUrl_argument_url_invalid_url_should_return_None
  → spiderfoot/sflib/core.py:180: useProxyForUrl(url)
    → spiderfoot/sflib/network.py:187: urlFQDN(url).lower()
      → AttributeError
```

### Required Actions
1. **Fix `spiderfoot/sflib/network.py:187`**:
   ```python
   # Before:
   host = urlFQDN(url).lower()
   
   # After:
   host = urlFQDN(url)
   if host is None:
       return False  # or raise exception
   host = host.lower()
   ```

2. **Add tests** for None handling in URL validation

3. **Audit all callers** of `urlFQDN()` for similar bugs

---

## Root Cause #5: External API Test Reliability
**Impact:** 3 Cisco Umbrella failures + potentially more
**Priority:** MEDIUM

### Problem
External API tests fail due to network issues, timeouts, or API availability. No retry logic or configurable timeouts.

### Evidence
```
ERROR: Unexpected HTTP response code None from Cisco Umbrella API
test_handleEvent_domain_found FAILED
test_query_domain_found FAILED
test_query_domain_not_found FAILED
```

### Required Actions
1. **Add retry/timeout configuration** to `.env`:
   ```bash
   API_TEST_MAX_RETRIES=3
   API_TEST_RETRY_DELAY=2
   API_TEST_TIMEOUT=10
   API_TEST_SKIP_ON_FAILURE=true
   ```

2. **Implement retry decorator** for all external API tests:
   ```python
   @pytest.mark.external_api
   @retry(max_attempts=3, delay=2)
   def test_external_api():
       ...
   ```

3. **Add pytest markers**:
   ```python
   # pytest.ini
   markers =
       external_api: tests that call external APIs
       slow: tests that take >1s
   ```

4. **Make external tests optional**:
   ```bash
   pytest -m "not external_api"  # Skip external API tests
   ```

5. **Apply to ALL external API modules**, not just Cisco Umbrella

---

## Secondary Issues

### 6. Enterprise Storage Test Assertions
- Mock expectations don't match actual behavior
- Likely cascading from PostgreSQL connection failures
- Fix after Root Cause #1 is resolved

### 7. Web Server Integration Test
- `test_l_arg_should_start_web_server` - timing/assertion issue
- May be related to PostgreSQL initialization delay

### 8. CLI Exit Codes
- `test_types_arg_should_print_types_and_exit` expects 0, got 255
- Exit code 255 indicates PostgreSQL connection error
- Will be fixed by Root Cause #1

---

## Implementation Priority

### Phase 1: Critical Database Issues
1. Remove all SQLite code
2. Implement Redis for temporary storage
3. Fix test database isolation
4. Update test fixtures for PostgreSQL-only

### Phase 2: Configuration & Architecture
1. Fix module opts/optdescs mismatch
2. Fix storage module configuration
3. Fix test environment isolation

### Phase 3: Reliability & Polish
1. Add URL validation null checks
2. Implement external API retry logic
3. Add configuration for timeouts/retries
4. Fix remaining secondary issues

---

## Environment Requirements

### Test Database Credentials
**Location:** Environment variable (required)
```bash
export SPIDERFOOT_DB_PASSWORD='your_password'
```

**Configuration:** `test/conftest.py` lines 13-24
- Host: `unified-postgres.blk.ing`
- Port: `5432`
- Database: `spiderfoot_test`
- Username: `spiderfoot`
- Password: From `$SPIDERFOOT_DB_PASSWORD`

**Setup:**
```bash
./test/setup_test_db.sh
```

### Redis Configuration
**Target:** `unified-redis.blk.ing` (assumed from PostgreSQL naming)
- Replace all SQLite usage for temporary storage
- Session data, cache, queue storage

---

## Files Requiring Changes

### Database Layer
- `spiderfoot/db/db_core.py` - Remove SQLite detection/support
- `spiderfoot/db/__init__.py` - Remove SQLite references
- `spiderfoot/db/db_config_builder.py` - Remove SQLite options
- `modules/sfp__stor_db.py` - PostgreSQL-only, add Redis support

### Test Configuration
- `test/conftest.py` - Fix env var isolation
- `pytest.ini` - Add markers, default config
- `test/fixtures/database_fixtures.py` - PostgreSQL fixtures

### Core Libraries
- `spiderfoot/sflib/network.py:187` - Add null check
- Module files (45+) - Fix opts/optdescs or config loading

### Documentation
- `test/README.md` - Update for PostgreSQL-only
- `documentation/POSTGRESQL_SETUP.md` - Remove SQLite references
- `.env.template` - Add API test configuration

---

## Success Metrics

- **Target:** 0 failures, 0 errors
- **Current:** 323 failures, 85 errors
- **Improvement:** 100% test pass rate
- **Performance:** Test suite completes in <25 minutes

---

## Notes for Agent Teams

1. **Database Team**: Focus on Root Cause #1 - this is blocking ~140 tests
2. **Config Team**: Address Root Cause #2 and #3 - architectural decisions needed
3. **Quality Team**: Handle Root Causes #4 and #5 - defensive coding and reliability
4. **Each team** should create a detailed implementation plan before starting
5. **Coordinate** on shared files (conftest.py, db layer)
