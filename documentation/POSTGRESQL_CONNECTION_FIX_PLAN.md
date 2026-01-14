# Fix PostgreSQL Database Connection Error in SpiderFoot

## Problem Summary

**Error**: `OSError: Error connecting to PostgreSQL database /home/spiderfoot/data/spiderfoot.db`

**Root Cause**: The PostgreSQL migration left SQLite fallback logic that creates SQLite-style file paths (`/home/spiderfoot/data/spiderfoot.db`) which fail when passed to `psycopg2.connect()`. Additionally, there are connection string format inconsistencies and duplicate connection logic.

## Critical Issues Found

1. **SQLite Fallback in Multiple Places** (PRIMARY BUG)
   - `/stuff/spiderfoot/sfwebui.py:167` - Falls back to SQLite path when env vars not set
   - `/stuff/spiderfoot/spiderfoot/webui/routes.py:1110` - Also creates SQLite path fallback
   - These SQLite paths fail with PostgreSQL since SQLite support was removed

2. **Connection String Format Mismatch**
   - `sf.py` uses DSN URI format: `postgresql://user:pass@host:port/database`
   - `sfwebui.py` uses key-value format: `host=localhost port=5432 dbname=spiderfoot`
   - Both are valid for psycopg2, but inconsistency causes confusion

3. **Duplicate Connection Logic**
   - `/stuff/spiderfoot/spiderfoot/db/__init__.py:364` - Creates connection after DbCore already created one at line 344
   - If second attempt fails, overwrites working connection

4. **Environment Variable Naming Inconsistencies**
   - API uses: `SPIDERFOOT_DB_NAME`, `SPIDERFOOT_DB_PASS`
   - CLI/WebUI use: `SPIDERFOOT_DB`, `SPIDERFOOT_DB_PASSWORD`

## Current Broken Dataflow Diagram

```mermaid
graph TD
    subgraph "Entry Points"
        A1[sf.py CLI Entry]
        A2[sfwebui.py Web Entry]
        A3[API dependencies.py]
    end

    subgraph "Configuration Layer - INCONSISTENT"
        B1["sf.py Lines 80-101<br/>Format: postgresql://user:pass@host:port/db<br/>Default: 'sqlite'"]
        B2["sfwebui.py Lines 151-167<br/>Format: host=X port=Y dbname=Z user=U password=P<br/>Default: 'sqlite'<br/>FALLBACK: /home/spiderfoot/data/spiderfoot.db"]
        B3["api/dependencies.py Lines 19-35<br/>Format: postgresql://user:pass@host:port/db<br/>Env vars: DB_NAME, DB_PASS"]
    end

    subgraph "WebUI Routes Layer - ADDITIONAL FALLBACK"
        C1["routes.py Lines 1100-1111<br/>FALLBACK: /home/spiderfoot/data/spiderfoot.db<br/>Sets __dbtype='sqlite'"]
    end

    subgraph "Database Layer - DUPLICATE CONNECTIONS"
        D1["db/__init__.py Line 344<br/>self._core = DbCore(opts, init)<br/>✓ Creates Connection #1"]
        D2["db/__init__.py Lines 364-369<br/>self.conn = psycopg2.connect(opts['__database'])<br/>✗ Creates Connection #2 (DUPLICATE)"]
        D3["db_core.py Lines 738-745<br/>psycopg2.connect(database_path)<br/>✓ Actual PostgreSQL Connection"]
    end

    subgraph "Database"
        E1[(PostgreSQL Database)]
    end

    A1 -->|reads env vars| B1
    A2 -->|reads env vars| B2
    A3 -->|reads env vars| B3

    B1 -->|opts dict| D1
    B2 -->|opts dict| C1
    B3 -->|opts dict| D1

    C1 -->|opts dict with<br/>SQLite path!| D1

    D1 -->|calls DbCore.__init__| D3
    D1 -.->|then duplicates!| D2

    D3 -->|Connection #1| E1
    D2 -->|Connection #2<br/>FAILS if SQLite path!| E1

    style B2 fill:#ffcccc
    style C1 fill:#ffcccc
    style D2 fill:#ffcccc
    style B1 fill:#ffffcc
    style B3 fill:#ffffcc

    classDef buggy fill:#ffcccc,stroke:#ff0000,stroke-width:2px
    classDef inconsistent fill:#ffffcc,stroke:#ffaa00,stroke-width:2px
    class B2,C1,D2 buggy
    class B1,B3 inconsistent
```

## Triplicated Configuration Logic

The configuration is built **3 separate times** with **3 different formats**:

### Path 1: CLI Entry (sf.py)
```
Environment Variables
   ↓
sf.py:80-101 (reads SPIDERFOOT_DB_*, defaults to 'sqlite')
   ↓
Constructs: postgresql://user:password@host:port/database
   ↓
Passes to SpiderFootDb
   ↓
DbCore creates connection #1 ✓
   ↓
db/__init__.py creates connection #2 ✗ (duplicate)
   ↓
PostgreSQL Database
```

### Path 2: WebUI Entry (sfwebui.py + routes.py)
```
Environment Variables
   ↓
sfwebui.py:151-167 (reads SPIDERFOOT_DB_*, defaults to 'sqlite')
   ↓
If PostgreSQL: host=localhost port=5432 dbname=X user=Y password=Z
If NOT: /home/spiderfoot/data/spiderfoot.db (SQLite path!)
   ↓
routes.py:1100-1111 (SECOND fallback check)
   ↓
If empty: /home/spiderfoot/data/spiderfoot.db (SQLite path!)
   ↓
Passes to SpiderFootDb
   ↓
DbCore creates connection #1 with SQLite path ✗ FAILS!
   ↓
db/__init__.py tries connection #2 with SQLite path ✗ FAILS AGAIN!
   ↓
ERROR: OSError: Error connecting to PostgreSQL database /home/spiderfoot/data/spiderfoot.db
```

### Path 3: API Entry (dependencies.py)
```
Environment Variables
   ↓
api/dependencies.py:19-35 (reads SPIDERFOOT_DB_NAME, SPIDERFOOT_DB_PASS)
   ↓
Constructs: postgresql://user:password@host:port/database
   ↓
Passes to SpiderFootDb
   ↓
DbCore creates connection #1 ✓
   ↓
db/__init__.py creates connection #2 ✗ (duplicate)
   ↓
PostgreSQL Database
```

## Implementation Plan

### Phase 1: Create Centralized Configuration Builder

**Goal**: Single source of truth for PostgreSQL configuration

**File**: Create `/stuff/spiderfoot/spiderfoot/db/db_config_builder.py`

**Purpose**:
- Centralize database configuration logic
- Standardize on DSN URI format (`postgresql://...`)
- Support both old and new environment variable names
- Provide clear error messages for missing configuration

**Key Features**:
- Function: `build_database_config()` - Returns dict with `__database` and `__dbtype`
- Function: `get_database_string()` - Returns just the DSN URI
- URL-encode passwords with special characters
- Validate required environment variables
- Default to PostgreSQL (no SQLite support)

### Phase 2: Update All Entry Points to Use Builder

**Goal**: Ensure consistent DSN URI format everywhere

**Files to Modify**:

1. **`/stuff/spiderfoot/sf.py`** (Lines 80-116)
   - Replace manual DSN construction with `build_database_config()`
   - Add clear error message for missing config
   - Exit with code 1 if config invalid

2. **`/stuff/spiderfoot/sfwebui.py`** (Lines 151-167)
   - Replace key-value format construction with `build_database_config()`
   - Remove SQLite fallback at line 167
   - Raise ValueError with helpful message if config missing

3. **`/stuff/spiderfoot/spiderfoot/api/dependencies.py`** (Lines 19-35)
   - Replace manual DSN construction with `build_database_config()`
   - Maintain support for `SPIDERFOOT_DATABASE` override

### Phase 3: Remove Duplicate Connection Logic

**Goal**: Fix double connection creation bug

**File**: `/stuff/spiderfoot/spiderfoot/db/__init__.py` (Lines 353-399)

**Changes**:
- **Remove lines 363-399** - Duplicate connection creation
- **Keep lines 344-352** - DbCore initialization and delegation
- DbCore already creates the connection correctly; no need to duplicate

### Phase 4: Remove SQLite Fallbacks

**Goal**: Eliminate all SQLite fallback paths

**Files to Modify**:

1. **`/stuff/spiderfoot/spiderfoot/webui/routes.py`** (Lines 1100-1111)
   - Remove SQLite fallback logic at lines 1108-1111
   - Raise clear error requiring PostgreSQL configuration

2. **`/stuff/spiderfoot/spiderfoot/core/config.py`** (Lines 73-86)
   - Remove default SQLite path construction
   - Let database config come from environment variables

### Phase 5: Improve Error Handling

**Goal**: Provide actionable error messages

**File**: `/stuff/spiderfoot/spiderfoot/db/db_core.py` (Lines 738-751)

**Changes**:
- Add DSN URI format validation before connection attempt
- Catch `psycopg2.OperationalError` specifically for connection failures
- Provide detailed troubleshooting steps in error message
- Include connection parameters (sanitized) in error output

### Phase 6: Update Documentation

**Files to Create/Update**:

1. Create `/stuff/spiderfoot/docs/POSTGRESQL_SETUP.md`
   - Document all environment variables
   - Provide Docker and standalone setup examples
   - Include troubleshooting section

2. Update `/stuff/spiderfoot/.env.template`
   - Add SpiderFoot-specific database variables
   - Reference both old and new variable names for compatibility

3. Verify `/stuff/spiderfoot/docker-compose.yml.stub`
   - Ensure environment variables use consistent naming

## Environment Variables (Standardized)

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `SPIDERFOOT_DB_TYPE` | postgresql | No | Must be 'postgresql' |
| `SPIDERFOOT_DB_HOST` | localhost | No | PostgreSQL hostname |
| `SPIDERFOOT_DB_PORT` | 5432 | No | PostgreSQL port |
| `SPIDERFOOT_DB_NAME` or `SPIDERFOOT_DB` | - | **YES** | Database name |
| `SPIDERFOOT_DB_USER` | spiderfoot | No | Database username |
| `SPIDERFOOT_DB_PASSWORD` or `SPIDERFOOT_DB_PASS` | - | Recommended | Database password |

## Implementation Order

**Critical**: Follow this sequence to avoid breaking existing code

1. Create `db_config_builder.py` (new file, no dependencies)
2. Update `sf.py` to use builder
3. Update `sfwebui.py` to use builder
4. Update `api/dependencies.py` to use builder
5. Remove duplicate connection in `db/__init__.py`
6. Remove SQLite fallback in `routes.py`
7. Remove SQLite fallback in `core/config.py`
8. Improve error handling in `db_core.py`
9. Update documentation files

## Testing Strategy

**Unit Tests**:
- Test `db_config_builder.py` with various env var combinations
- Test password URL encoding
- Test error messages for missing configuration

**Integration Tests**:
- Test actual PostgreSQL connection
- Test all three entry points (CLI, WebUI, API)
- Test connection failure scenarios

**Manual Verification**:
- Verify error message when `SPIDERFOOT_DB_NAME` is missing
- Verify connection works with all env vars set
- Verify password special characters are handled correctly

## Immediate Workaround (For User)

While waiting for code fixes, set these environment variables:

```bash
export SPIDERFOOT_DB_TYPE=postgresql
export SPIDERFOOT_DB_HOST=localhost
export SPIDERFOOT_DB_PORT=5432
export SPIDERFOOT_DB_NAME=spiderfoot_db
export SPIDERFOOT_DB_USER=spiderfoot
export SPIDERFOOT_DB_PASSWORD=your_password
```

Or in Docker:
```yaml
environment:
  - SPIDERFOOT_DB_TYPE=postgresql
  - SPIDERFOOT_DB_HOST=postgres
  - SPIDERFOOT_DB_NAME=spiderfoot_db
  - SPIDERFOOT_DB_USER=spiderfoot
  - SPIDERFOOT_DB_PASSWORD=your_password
```

## Success Criteria

- [ ] No SQLite fallback paths remain in codebase
- [ ] All entry points use identical DSN URI format
- [ ] Clear error message when PostgreSQL config missing
- [ ] Connection created only once (via DbCore)
- [ ] Environment variable naming documented (both old/new supported)
- [ ] Tests pass with new configuration
- [ ] Production error resolved

## Risk Mitigation

**Breaking Changes**: Existing deployments relying on SQLite fallback will break
- **Mitigation**: Add startup validation with clear error messages

**Connection Failures**: Invalid DSN format could break connections
- **Mitigation**: Add DSN format validation before connection attempt

**Password Special Characters**: Passwords with `@`, `:`, `/` could break URI
- **Mitigation**: Use `urllib.parse.quote_plus()` for URL encoding

## Files to Modify (Summary)

1. `/stuff/spiderfoot/spiderfoot/db/db_config_builder.py` - **NEW FILE** (centralized config)
2. `/stuff/spiderfoot/spiderfoot/db/__init__.py` - Remove duplicate connection (lines 363-399)
3. `/stuff/spiderfoot/sfwebui.py` - Use builder, remove SQLite fallback (lines 151-167)
4. `/stuff/spiderfoot/sf.py` - Use builder (lines 80-116)
5. `/stuff/spiderfoot/spiderfoot/webui/routes.py` - Remove SQLite fallback (lines 1108-1111)
6. `/stuff/spiderfoot/spiderfoot/db/db_core.py` - Improve error messages (lines 738-751)
7. `/stuff/spiderfoot/spiderfoot/api/dependencies.py` - Use builder (lines 19-35)
8. `/stuff/spiderfoot/spiderfoot/core/config.py` - Remove SQLite path (lines 73-86)
9. `/stuff/spiderfoot/docs/POSTGRESQL_SETUP.md` - **NEW FILE** (documentation)
10. `/stuff/spiderfoot/.env.template` - Add SpiderFoot DB variables
