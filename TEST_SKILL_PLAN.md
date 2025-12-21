# SpiderFoot Test Skill Implementation Plan

## Executive Summary

Create a comprehensive `/test` skill for Claude Code that provides flexible test execution with built-in quality gates, pre-commit hooks, Redis-based coordination, and integration with existing linters and validators from `/stuff/coding_standards`.

**User Requirements:**
- Pre-commit hook (tests must pass before commits)
- Periodic test reminder (scheduled execution)
- Regression test gate (blocks changes without regression tests)
- Block commits when tests fail (strict enforcement)
- Redis coordination for parallel test execution and caching

**Redis Infrastructure:**
- Existing `unified-redis` container in `/stuff/blking_local_proxy/docker-compose.yml`
- Currently internal to `blking_private_network` only
- **SETUP REQUIRED:** Add Traefik labels to expose through internal-proxy
- Access from host via `redis.blking.lan` (or ${INTERNAL_DOMAIN}) after proxy configuration

## 1. Redis Proxy Configuration (PREREQUISITE)

### 1.1 Add Traefik Labels to unified-redis

**File:** `/stuff/blking_local_proxy/docker-compose.yml`

Add the following labels to the `unified-redis` service (after line 60):

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=blking_private_network"
  - "traefik.http.routers.redis.rule=Host(`redis.${INTERNAL_DOMAIN}`)"
  - "traefik.http.services.redis.loadbalancer.server.port=6379"
  - "traefik.http.routers.redis.entrypoints=websecure"
  - "traefik.http.routers.redis.tls=true"
  - "SERVICE_6379_NAME=unified-redis"
  - "SERVICE_TAGS=internal,cache,coordination,production"
```

### 1.2 Redis Access Pattern

**From Host (tests):**
- Hostname: `redis.blk.ing`
- Port: 6379 (TCP through Traefik)
- Connection: `redis-cli -h redis.blk.ing -p 6379`

**From Containers:**
- Hostname: `redis` or `unified-redis`
- Port: 6379
- Connection: `redis-cli -h redis -p 6379`

### 1.3 Redis Coordination Features

**Test Result Caching:**
- Key: `test:cache:{file_hash}:{test_name}`
- Value: `{status}:{duration}:{timestamp}`
- TTL: 3600 (1 hour)

**Parallel Test Coordination:**
- Key: `test:lock:{test_suite}`
- Value: `{worker_id}:{pid}:{timestamp}`
- Used to prevent duplicate test execution

**Test History Tracking:**
- Key: `test:history:{date}`
- Value: JSON of test results
- Used for trend analysis

**Last Test Run:**
- Key: `test:last_run`
- Value: Unix timestamp
- Used for periodic reminder system

## 2. Core Test Skill (`/test`)

### 2.1 Skill File Location
**Primary File:** `/stuff/spiderfoot/.claude/commands/test.md`

### 2.2 Test Execution Modes

```bash
/test                          # Interactive menu (show available modes)
/test unit                     # Unit tests only
/test integration              # Integration tests (excluding modules)
/test integration --modules    # Integration tests (including modules)
/test regression               # Regression tests only
/test acceptance               # Acceptance tests (Robot Framework)
/test all                      # All tests
/test <path>                   # Specific file/directory
/test -k <pattern>             # Pattern matching
```

### 2.3 Skill Options

```bash
--parallel              # Use pytest-xdist with all CPU cores
--cov                   # Generate coverage report (HTML + terminal)
--verbose / -v          # Verbose output
--db=sqlite|postgres    # Database backend
--durations=N           # Show N slowest tests
--quick                 # Fast subset (unit only, no coverage)
--strict                # Fail on warnings
--markers=EXPR          # Run tests matching pytest markers
```

### 2.4 Test Infrastructure Integration

**Database Configuration:**
```bash
# SQLite (default)
SF_DB_TYPE=sqlite
SF_DB_PATH=/stuff/spiderfoot/test_spiderfoot.db

# PostgreSQL (optional)
SF_DB_TYPE=postgresql
SF_PG_HOST, SF_PG_PORT, SF_PG_DB, SF_PG_USER, SF_PG_PASS
```

**Test Framework:** pytest 8.4.1 with plugins
- pytest-xdist (parallel execution)
- pytest-cov (coverage reporting)
- pytest-mock (mocking)

**Test Organization:**
- `test/unit/` - 272+ unit tests
- `test/integration/` - 238+ integration tests
- `test/regression/` - 3 regression tests
- `test/acceptance/` - 4 Robot Framework tests

### 2.5 Output Report Format

```markdown
## Test Execution Summary

**Mode:** Unit Tests
**Database:** SQLite
**Parallel:** Yes (8 workers)
**Coverage:** 85%
**Duration:** 45.23s

### Results
✅ Passed: 284 tests
❌ Failed: 2 tests
⏭️  Skipped: 3 tests

### Failed Tests
1. test/unit/test_sfwebui.py::test_settings_persistence
   AssertionError: Expected 'postgresql' but got 'sqlite'

### Coverage Report
📊 HTML Report: /stuff/spiderfoot/htmlcov/index.html

### Quality Gates
✅ Coverage threshold: 85% (target: 80%)
✅ No critical warnings
❌ 2 tests failed - BLOCKING COMMIT

### Next Steps
- Fix failed tests before committing
- Run: /test test/unit/test_sfwebui.py::test_settings_persistence -v
```

## 3. Git Pre-Commit Hook

### 3.1 Hook File Location
**File:** `/stuff/spiderfoot/.git/hooks/pre-commit`

### 3.2 Hook Behavior

**Smart Test Selection:**
1. Detect changed files (`git diff --cached --name-only`)
2. Run tests related to changed files:
   - Changed `spiderfoot/*.py` → Run unit tests
   - Changed `test/` → Run those specific tests
   - Changed `spiderfoot/correlation/` → Run correlation + regression tests
   - Changed `spiderfoot/db/` → Run database + regression tests

**Validation Steps:**
1. Run shellcheck on any changed `.sh` files (MANDATORY FIRST)
2. Run flake8 on changed `.py` files
3. Run relevant pytest tests
4. Check coverage threshold (80% minimum)
5. Validate any changed YAML files against schemas

**Blocking Conditions:**
- Any test fails → BLOCK COMMIT
- shellcheck fails → BLOCK COMMIT
- flake8 errors → BLOCK COMMIT
- Schema validation fails → BLOCK COMMIT
- Coverage warning only (not blocking)

**User Override:**
```bash
# Emergency bypass (discouraged)
git commit --no-verify
```

### 3.3 Hook Integration with Existing Tools

**MANDATORY: shellcheck for All Shell Scripts:**
- shellcheck is REQUIRED for all .sh files and git hooks
- No shell script commits allowed without passing shellcheck
- All hooks must be shellcheck-validated before installation
- Pre-commit hook itself must pass shellcheck
- shellcheck runs FIRST before any other validation

**Leverage `/stuff/coding_standards/master-linter-setup.sh`:**
- Use installed linters (pylint, flake8, shellcheck)
- Follow coding standards from `/stuff/coding_standards/python-coding-standards.md`

**Schema Validation:**
- Use schemas from `/stuff/coding_standards/schemas/`
- Validate YAML correlation rules against schema
- Validate JSON configs against mcp-config.schema.json

## 4. Linter and Validator Integration

### 4.1 Python Linting (Already Configured)

**Tools Used (from test/requirements.txt):**
- flake8 v7.3.0 with plugins:
  - flake8-annotations (type hints)
  - flake8-blind-except (exception handling)
  - flake8-bugbear (common bugs)
  - flake8-builtins (builtin shadowing)
  - flake8-quotes (quote consistency)
  - flake8-return (return statement issues)
  - flake8-simplify (simplification opportunities)
- darglint (docstring validation)
- dlint (security linting)

**Configuration (setup.cfg):**
```ini
[flake8]
max-line-length = 120
max-complexity = 60
docstring-convention = google
select = C,E,F,W,B,B9,DAR,DUO,R,A,S,Q0,SIM,SFS
```

### 4.2 Pre-Commit Linting Workflow

```bash
# 0. MANDATORY: shellcheck first (for hooks and scripts)
changed_sh=$(git diff --cached --name-only --diff-filter=ACM | grep '\.sh$')
if [ -n "$changed_sh" ]; then
    echo "🔍 shellcheck (MANDATORY)..."
    shellcheck $changed_sh || {
        echo "❌ shellcheck FAILED - COMMIT BLOCKED"
        echo "Fix shell script issues before committing"
        exit 1
    }
fi

# 1. Get changed Python files
changed_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

# 2. Run flake8 on changed files
if [ -n "$changed_files" ]; then
    echo "🔍 flake8..."
    flake8 $changed_files || {
        echo "❌ flake8 FAILED - COMMIT BLOCKED"
        exit 1
    }
fi

# 3. Run bandit for security checks
if [ -n "$changed_files" ]; then
    echo "🔍 bandit (security)..."
    bandit -r spiderfoot/ -f json -o bandit-report.json || {
        echo "⚠️  Security issues detected - review bandit-report.json"
        # Warning only for now, can make blocking later
    }
fi
```

### 4.3 Schema Validation Integration

**Correlation YAML Validation:**
```bash
# Use existing regression test
pytest test/regression/test_correlation_schema_validation.py -v
```

**JSON Config Validation:**
```bash
# Validate against schemas in /stuff/coding_standards/schemas/json/
jsonschema -i .mcp.json /stuff/coding_standards/schemas/json/custom/mcp-config.schema.json
```

## 5. Periodic Test Reminder System

### 5.1 Implementation Approach

**Option A: Cron Job (Recommended)**

**File:** `/stuff/spiderfoot/.claude/scripts/test-reminder.sh`

```bash
#!/bin/bash
# Daily test reminder - runs at 9 AM

cd /stuff/spiderfoot

# Check last test run from Redis
last_run=$(redis-cli -h redis.blking.lan -p 443 --tls GET test:last_run)
days_ago=$(( ($(date +%s) - $last_run) / 86400 ))

if [ $days_ago -ge 1 ]; then
    echo "⚠️  Tests haven't run in $days_ago days!"
    echo "Run: /test unit --quick"
fi
```

**Cron Entry:**
```bash
0 9 * * * /stuff/spiderfoot/.claude/scripts/test-reminder.sh
```

**Option B: Git Hook (post-merge)**

**File:** `/stuff/spiderfoot/.git/hooks/post-merge`

```bash
#!/bin/bash
# Run tests after merging/pulling changes

echo "🔄 Running tests after merge..."
pytest test/regression/ -v
```

### 5.2 Test Run Tracking

**Redis Key:** `test:last_run`
- Updated after each test execution via pre-commit hook
- Contains Unix timestamp
- Used by reminder system

## 6. Regression Test Gate

### 6.1 Gate Behavior

**Trigger:** Before allowing commits that modify core functionality

**Validation:**
1. Identify modified files
2. Check if regression tests exist for modified areas
3. Run existing regression tests
4. Require all regression tests to pass

**Gate Logic:**
```bash
# Check if core functionality changed
if git diff --cached --name-only | grep -E "(spiderfoot/db|spiderfoot/correlation|spiderfoot/webui)"; then
    echo "🔒 Core functionality changed - running regression tests..."

    pytest test/regression/ -v || {
        echo "❌ Regression tests failed - COMMIT BLOCKED"
        echo "Fix regressions or update tests before committing"
        exit 1
    }
fi
```

### 6.2 Regression Coverage Check

**Ensure All Regressions Have Tests:**
```bash
# Use existing regression validation
pytest test/regression/test_correlation_schema_validation.py
pytest test/regression/test_database_settings_persistence.py
pytest test/regression/test_webui_settings_form_submission.py
```

**New Regression Workflow:**
1. Bug discovered → Create regression entry with `/regression-track`
2. Write regression test
3. Pre-commit hook ensures test passes before allowing commit
4. Regression gate prevents removing/breaking tests

## 7. Coverage Threshold Enforcement

### 7.1 Coverage Requirements

**Minimum Coverage:** 80%
**Coverage Report Location:** `/stuff/spiderfoot/htmlcov/index.html`

### 7.2 Pre-Commit Coverage Check

```bash
# Run tests with coverage
pytest test/unit/ --cov=spiderfoot --cov-report=term --cov-report=html -q

# Parse coverage percentage
coverage=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')

if [ "${coverage%%.*}" -lt 80 ]; then
    echo "⚠️  Coverage ${coverage}% below 80% threshold"
    echo "Consider adding tests to improve coverage"
    # Warning only, don't block
fi
```

## 8. File Structure

### 8.1 Files to Create

```
/stuff/spiderfoot/
├── .claude/
│   ├── commands/
│   │   └── test.md                    # Main test skill (NEW)
│   └── scripts/
│       ├── test-runner.sh             # Test execution helper (NEW)
│       ├── test-reminder.sh           # Periodic reminder (NEW)
│       └── pre-commit-tests.sh        # Pre-commit test logic (NEW)
├── .git/
│   └── hooks/
│       ├── pre-commit                 # Pre-commit hook (NEW)
│       └── post-merge                 # Post-merge hook (NEW)
└── TEST_SKILL_PLAN.md                 # This document
```

### 8.2 Files to Reference (Existing)

```
/stuff/spiderfoot/
├── test/
│   ├── run                            # Existing test runner
│   ├── conftest.py                    # pytest configuration
│   ├── requirements.txt               # Test dependencies
│   ├── unit/                          # 272 unit tests
│   ├── integration/                   # 238 integration tests
│   ├── regression/                    # 3 regression tests
│   └── acceptance/                    # 4 acceptance tests
├── setup.cfg                          # flake8 configuration
└── sonar-project.properties           # SonarQube config

/stuff/coding_standards/
├── master-linter-setup.sh             # Linter installation
├── linter-configuration-guide.md      # Linter docs
├── python-coding-standards.md         # Python standards
└── schemas/                           # Validation schemas
    ├── json/
    │   ├── official/
    │   └── custom/
    │       ├── mcp-config.schema.json
    │       └── marketplace.schema.json
    └── yaml/

/stuff/blking_local_proxy/
└── docker-compose.yml                 # Redis infrastructure (TO MODIFY)
```

## 9. Implementation Steps

### Phase 0: Redis Proxy Setup (PREREQUISITE)
1. Edit `/stuff/blking_local_proxy/docker-compose.yml`
2. Add Traefik labels to `unified-redis` service (see section 1.1)
3. Restart containers: `cd /stuff/blking_local_proxy && docker-compose up -d unified-redis internal-proxy`
4. Test Redis access from host: `redis-cli -h redis.blking.lan -p 443 --tls PING`
5. Verify response: `PONG`

### Phase 1: Core Test Skill
1. Create `/stuff/spiderfoot/.claude/commands/test.md`
2. Implement argument parsing logic
3. Add test mode handlers (unit, integration, regression, acceptance, all)
4. Add database configuration setup
5. Add Redis coordination helpers (caching, locking, history)
6. Implement result parsing and reporting
7. Test all execution modes

### Phase 2: Pre-Commit Hook
1. Create `/stuff/spiderfoot/.claude/scripts/pre-commit-tests.sh`
2. **VALIDATE with shellcheck** (pre-commit-tests.sh must pass shellcheck)
3. Implement smart file change detection
4. Add MANDATORY shellcheck execution first
5. Add linter execution (flake8)
6. Add schema validation
7. Add test execution logic
8. Add coverage threshold check (warning only)
9. Add Redis last-run tracking
10. Create `/stuff/spiderfoot/.git/hooks/pre-commit`
11. **VALIDATE hook with shellcheck** (pre-commit must pass shellcheck)
12. Make hook executable: `chmod +x /stuff/spiderfoot/.git/hooks/pre-commit`
13. Test with sample commits

### Phase 3: Regression Gate
1. Add regression detection logic to pre-commit hook
2. Ensure all regression tests run for core changes
3. Block commits if regression tests fail
4. Test with core file modifications

### Phase 4: Periodic Reminders
1. Create `/stuff/spiderfoot/.claude/scripts/test-reminder.sh`
2. **VALIDATE with shellcheck**
3. Implement test run tracking via Redis
4. Set up cron job or post-merge hook
5. Test reminder notifications

### Phase 5: Integration & Documentation
1. Update skill with examples
2. Document hook behavior
3. Create override procedures
4. Test complete workflow
5. Update this plan document with any changes

## 10. Success Criteria

### Skill Functionality
- [ ] All test modes execute correctly
- [ ] Options work as expected
- [ ] Reports are clear and actionable
- [ ] Error messages are helpful
- [ ] Redis coordination works

### Git Hook Functionality
- [ ] **CRITICAL: All shell scripts pass shellcheck (mandatory)**
- [ ] Pre-commit hook itself passes shellcheck
- [ ] Pre-commit hook blocks bad commits
- [ ] Smart test selection works
- [ ] Linters run correctly (shellcheck first, then flake8)
- [ ] Coverage threshold enforced (warning)
- [ ] Redis last-run tracking works

### Regression Gate
- [ ] Regression tests run for core changes
- [ ] Gate blocks commits on failures
- [ ] All regressions have tests

### Periodic Reminders
- [ ] Reminder script passes shellcheck
- [ ] Reminder script tracks test runs via Redis
- [ ] Notifications appear appropriately
- [ ] Integration with cron/hooks works

### shellcheck Validation (MANDATORY)
- [ ] All .sh files in repo pass shellcheck
- [ ] All git hooks pass shellcheck
- [ ] All scripts in .claude/scripts/ pass shellcheck
- [ ] shellcheck runs before other linters in pre-commit
- [ ] shellcheck failures block commits

### Redis Integration
- [ ] Traefik labels added to unified-redis
- [ ] Redis accessible from host via redis.blking.lan
- [ ] Test result caching works
- [ ] Test history tracking works
- [ ] Last run tracking works

### Integration
- [ ] Works with existing test infrastructure
- [ ] Uses existing linters and schemas
- [ ] Compatible with pytest configuration
- [ ] Doesn't break existing workflows

## 11. Edge Cases and Considerations

### Hook Bypass
- Allow `git commit --no-verify` for emergencies
- Log bypasses for audit trail
- Warn user about risks

### Long-Running Tests
- Pre-commit should complete in <30 seconds
- Use smart selection, not full test suite
- Provide option to run full tests manually via `/test all`

### Coverage Fluctuation
- Coverage check is warning, not blocker
- Full coverage check via CI/CD
- Pre-commit focuses on test failures

### Schema Updates
- If schema changes, update validators
- Ensure backward compatibility
- Version schemas appropriately

### Multiple Commits
- Hook runs on each commit
- May be repetitive for small changes
- Consider batch mode for series of fixes

### Redis Unavailability
- Graceful fallback if Redis not accessible
- Don't block tests if coordination fails
- Log Redis errors but continue

## 12. Future Enhancements

1. **Test Result Caching via Redis**
   - Cache results for unchanged files
   - Speed up repeated runs
   - TTL: 1 hour

2. **Parallel Lint + Test**
   - Run linters and tests concurrently
   - Reduce pre-commit wait time

3. **Visual Progress Bar**
   - Show test execution progress
   - Estimate completion time

4. **Test History Dashboard**
   - Track test trends over time via Redis
   - Identify flaky tests
   - Performance regression detection

5. **Auto-Fix Suggestions**
   - Suggest fixes for common failures
   - Offer to auto-format code
   - Generate skeleton tests

6. **Distributed Test Execution**
   - Use Redis for coordinating parallel workers
   - Run tests across multiple machines
   - Load balancing

## 13. Critical Files Summary

**To Create:**
1. `/stuff/spiderfoot/.claude/commands/test.md` - Main test skill
2. `/stuff/spiderfoot/.claude/scripts/pre-commit-tests.sh` - Test logic
3. `/stuff/spiderfoot/.git/hooks/pre-commit` - Git hook
4. `/stuff/spiderfoot/.claude/scripts/test-reminder.sh` - Reminder script

**To Modify:**
1. `/stuff/blking_local_proxy/docker-compose.yml` - Add Redis Traefik labels

**To Reference:**
1. `/stuff/spiderfoot/test/run` - Existing test patterns
2. `/stuff/spiderfoot/test/conftest.py` - pytest configuration
3. `/stuff/spiderfoot/setup.cfg` - flake8 configuration
4. `/stuff/coding_standards/master-linter-setup.sh` - Linter tools
5. `/stuff/coding_standards/schemas/` - Validation schemas

**Integration Points:**
1. pytest (existing test framework)
2. flake8 (existing linter)
3. shellcheck (MANDATORY for all shell scripts)
4. Coverage.py (existing coverage tool)
5. Git hooks (standard Git mechanism)
6. Redis (coordination and caching)
7. Correlation schema validation (existing regression test)

---

**Implementation Complexity:** Medium-High
**Estimated Effort:** 4-6 hours
**Risk Level:** Low (builds on existing infrastructure)
**Impact:** High (comprehensive quality gates with Redis coordination)

**Plan Created:** 2025-12-20
**Plan Location:** `/stuff/spiderfoot/TEST_SKILL_PLAN.md`
