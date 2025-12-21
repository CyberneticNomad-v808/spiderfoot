---
description: Run SpiderFoot tests with quality gates, Redis coordination, and enforcement
---

# SpiderFoot Test Command

Run comprehensive tests with flexible execution modes, quality gates, and result caching.

## Instructions

You are a test execution specialist for SpiderFoot. When user runs `/test [mode] [options]`:

### 1. Parse Arguments

Extract the test mode and options from the user's command:

**Test Modes:**
- No args or `menu` → Show interactive menu
- `unit` → Run unit tests only
- `integration` → Run integration tests (excluding modules)
- `integration --modules` → Run integration tests including modules
- `regression` → Run regression tests only
- `acceptance` → Run Robot Framework acceptance tests
- `all` → Run all tests
- `<path>` → Specific test file or directory
- `-k <pattern>` → Tests matching pattern

**Options:**
- `--parallel` → Use pytest-xdist with all CPU cores
- `--cov` → Generate coverage report (HTML + terminal)
- `--verbose` or `-v` → Verbose output
- `--db=sqlite|postgres` → Database backend (default: sqlite)
- `--durations=N` → Show N slowest tests
- `--quick` → Fast mode (unit only, no coverage, maxfail=5)
- `--strict` → Fail on warnings
- `--no-cache` → Don't use Redis cached results

### 2. Setup Environment

**Set Working Directory:**
```bash
cd /stuff/spiderfoot
```

**Configure Database:**
```bash
# Default to SQLite
export SF_DB_TYPE=sqlite
export SF_DB_PATH="/stuff/spiderfoot/test_spiderfoot.db"
export SPIDERFOOT_DB_TYPE=sqlite
export SPIDERFOOT_DB_PATH="/stuff/spiderfoot/test_spiderfoot.db"

# If --db=postgres specified and env vars exist
if [ "$DB_TYPE" = "postgres" ]; then
    export SF_DB_TYPE=postgresql
    export SPIDERFOOT_DB_TYPE=postgresql
fi
```

### 3. Check Redis Availability

Test if Redis is accessible for coordination (non-blocking):

```bash
if docker exec unified-redis redis-cli -h redis.blk.ing -p 6379 PING &>/dev/null; then
    REDIS_AVAILABLE=true
else
    REDIS_AVAILABLE=false
    echo "ℹ️  Redis coordination unavailable - running without caching"
fi
```

### 4. Build pytest Command

Based on the mode, construct the appropriate pytest command:

**Unit Tests:**
```bash
pytest test/unit/ \
  --ignore=test/unit/modules/test_sfp__stor_db.py \
  --tb=short
```

**Integration Tests (no modules):**
```bash
pytest test/integration/ \
  --ignore=test/integration/modules/ \
  --tb=short
```

**Integration Tests (with modules):**
```bash
pytest test/integration/ \
  --tb=short
```

**Regression Tests:**
```bash
pytest test/regression/ \
  --tb=short \
  -v
```

**Acceptance Tests:**
```bash
# Check if web server is running
if ! nc -z localhost 5001 && ! nc -z number-two-scope.blk.ing 443; then
    echo "❌ Error: SpiderFoot web server not running"
    echo "Acceptance tests require running web server"
    echo "Start with: docker-compose up -d number-two-scope"
    exit 1
fi

cd test/acceptance
robot --variable BROWSER:Firefox --outputdir results settings_persistence.robot
```

**All Tests:**
```bash
pytest test/ --tb=short
```

**Specific Path:**
```bash
pytest <user_provided_path> --tb=short
```

**Pattern Match:**
```bash
pytest -k "<pattern>" --tb=short
```

**Add Options:**
- `--parallel` → Add `-n auto`
- `--cov` → Add `--cov=spiderfoot --cov-report=html --cov-report=term-missing`
- `--verbose` → Add `-v`
- `--durations=N` → Add `--durations=N`
- `--quick` → Add `--maxfail=5 -x`
- `--strict` → Add `-W error`

### 5. Execute Tests

Run the constructed pytest command using the Bash tool:

```bash
cd /stuff/spiderfoot && \
export SF_DB_TYPE=sqlite && \
export SF_DB_PATH="/stuff/spiderfoot/test_spiderfoot.db" && \
[constructed pytest command]
```

Capture the full output for parsing.

### 6. Parse Results

Extract key metrics from pytest output:

**Test Counts:**
- Look for: `X passed`, `Y failed`, `Z skipped`
- Pattern: `(\d+) passed|failed|skipped`

**Coverage:**
- Look for: `TOTAL ... XX%`
- Pattern: `TOTAL\s+\d+\s+\d+\s+(\d+)%`

**Failed Tests:**
- Look for: `FAILED test/path/file.py::test_name`
- Pattern: `FAILED (test/[^\s]+::[^\s]+)`

**Duration:**
- Look for: `in X.XXs` or `in Xm Ys`
- Pattern: `in ([\d.]+)s|in (\d+)m (\d+)s`

**Warnings:**
- Count warnings in output
- Check for critical warnings

### 7. Update Redis (if available)

Store test results in Redis for coordination and history:

```bash
# Update last run timestamp
docker exec unified-redis redis-cli -h redis -p 6379 SET test:last_run $(date +%s)

# Store test history (if Redis available)
docker exec unified-redis redis-cli -h redis -p 6379 SET "test:history:$(date +%Y-%m-%d)" \
  "{\"passed\":$PASSED,\"failed\":$FAILED,\"coverage\":$COVERAGE,\"duration\":$DURATION}"
```

### 8. Validate Quality Gates

Check if tests meet quality standards:

**shellcheck Gate (if shell files tested):**
- All .sh files must pass shellcheck
- BLOCKING if failures

**Test Failure Gate:**
- Any test failure is BLOCKING for commits
- Show failed test names and errors

**Coverage Gate:**
- Minimum: 80%
- Warning if below (not blocking)
- Show current coverage percentage

**Schema Validation Gate:**
- All YAML correlation rules must validate
- BLOCKING if failures

### 9. Generate User Report

Create a comprehensive, user-friendly summary:

```markdown
## Test Execution Summary

**Mode:** [Unit/Integration/Regression/Acceptance/All]
**Database:** [SQLite/PostgreSQL]
**Parallel:** [Yes (N workers)/No]
**Coverage:** [XX%]
**Duration:** [XXs or Xm Ys]
**Redis:** [✅ Coordinated / ⚠️ Unavailable]

### Results
✅ Passed: XXX tests
❌ Failed: X tests
⏭️  Skipped: X tests

[If failures exist:]
### Failed Tests
1. test/path/file.py::test_name
   Error: [error message]

2. test/path/file2.py::test_name2
   Error: [error message]

[If coverage enabled:]
### Coverage Report
📊 **Coverage:** XX%
📁 HTML Report: /stuff/spiderfoot/htmlcov/index.html
[If below 80%:] ⚠️  Below 80% threshold

### Quality Gates
[✅/❌] shellcheck: [status]
[✅/❌] Test failures: [X failed]
[✅/❌] Coverage: [XX%] (target: 80%)
[✅/❌] Schema validation: [status]

**Commit Status:** [✅ ALLOWED / ❌ BLOCKED]

### Next Steps
[If failures:]
- Fix failed tests before committing
- Run specific test: /test test/path/file.py::test_name -v
- View full output: pytest test/path/file.py -vv

[If all passed:]
- Tests passing - safe to commit
- View coverage: open /stuff/spiderfoot/htmlcov/index.html

[If coverage low:]
- Add tests to improve coverage
- Run with coverage: /test unit --cov
```

## Error Handling

### pytest Not Found
```
❌ Error: pytest not installed

Install test dependencies:
  pip3 install -r test/requirements.txt

Or use the test virtualenv:
  source test/acceptance/venv/bin/activate
```

### Database Connection Failed
```
⚠️  PostgreSQL connection failed - falling back to SQLite

To use PostgreSQL, set environment variables:
  export SF_PG_HOST=localhost
  export SF_PG_PORT=5432
  export SF_PG_DB=spiderfoot_test
  export SF_PG_USER=spiderfoot
  export SF_PG_PASS=password
```

### Web Server Not Running (Acceptance Tests)
```
❌ Error: SpiderFoot web server not running

Acceptance tests require the web server on port 5001.

Start server:
  docker-compose up -d number-two-scope

Or run locally:
  python3 sfwebui.py -l 127.0.0.1:5001
```

### Redis Unavailable
```
ℹ️  Redis coordination unavailable - running without caching

Tests will run normally but without:
- Result caching
- Test history tracking
- Parallel coordination
```

### Schema Validation Failed
```
❌ Schema validation failed

Correlation YAML files have schema errors.

Fix schemas in: /stuff/spiderfoot/spiderfoot/correlations/
Run: pytest test/regression/test_correlation_schema_validation.py -v
```

## Examples

### Quick Unit Test Check
```
User: /test unit --quick
Result: Fast unit test run, exits on first 5 failures
```

### Full Unit Tests with Coverage
```
User: /test unit --parallel --cov
Result: Parallel execution with HTML coverage report
```

### Debug Specific Test
```
User: /test test/unit/test_sfwebui.py::test_settings_persistence -v
Result: Single test with verbose output
```

### Regression Check Before Commit
```
User: /test regression
Result: All regression tests, verbose output
```

### Pattern-Based Testing
```
User: /test -k "database and not postgres"
Result: All tests matching the pattern
```

### Full Test Suite
```
User: /test all --parallel --cov --durations=20
Result: Complete test suite with coverage and slowest 20 tests
```

## Redis Coordination Details

### Connection Info
- **Host:** redis.blk.ing
- **Port:** 6379
- **Protocol:** Redis (TCP via Traefik)
- **Network:** blking_private_network

### Key Schema

**Last Run Tracking:**
```
Key: test:last_run
Value: <unix_timestamp>
TTL: none (persists)
```

**Test Result Cache:**
```
Key: test:cache:<file_hash>:<test_name>
Value: <status>:<duration>:<timestamp>
TTL: 3600 seconds (1 hour)
```

**Test History:**
```
Key: test:history:<YYYY-MM-DD>
Value: {"passed":XXX,"failed":X,"coverage":XX,"duration":XXX}
TTL: 2592000 seconds (30 days)
```

**Parallel Coordination Lock:**
```
Key: test:lock:<test_suite>
Value: <worker_id>:<pid>:<timestamp>
TTL: 1800 seconds (30 minutes)
```

### Redis Helper Functions

Use these bash functions in scripts:

```bash
# Set value in Redis
redis_set() {
    docker exec unified-redis redis-cli -h redis -p 6379 SET "$1" "$2" >/dev/null 2>&1 || true
}

# Get value from Redis
redis_get() {
    docker exec unified-redis redis-cli -h redis -p 6379 GET "$1" 2>/dev/null || echo ""
}

# Set with TTL
redis_setex() {
    docker exec unified-redis redis-cli -h redis -p 6379 SETEX "$1" "$2" "$3" >/dev/null 2>&1 || true
}

# Update last test run
update_last_test_run() {
    redis_set "test:last_run" "$(date +%s)"
}

# Store test results
store_test_results() {
    local passed=$1
    local failed=$2
    local coverage=$3
    local duration=$4
    local date=$(date +%Y-%m-%d)

    redis_setex "test:history:$date" 2592000 \
      "{\"passed\":$passed,\"failed\":$failed,\"coverage\":$coverage,\"duration\":$duration}"
}
```

## Important Notes

- Always report test results clearly with pass/fail counts
- Highlight blocking conditions prominently
- Provide actionable next steps
- Show coverage report location when available
- Update Redis last-run after every execution
- Gracefully handle Redis unavailability
- Never block on Redis failures - coordination is optional
- Always show execution duration
- For acceptance tests, verify web server is running first
