# PostgreSQL Compatibility Fix - Complete Reference Document

**Version:** 1.0
**File:** /stuff/spiderfoot/spiderfoot/db.py
**Date:** 2025-10-06
**Total Issues:** 11 categories across 14+ locations

---

## Executive Summary

The SpiderFoot database layer (db.py) contains multiple SQLite-specific constructs that prevent PostgreSQL compatibility. These issues fall into the following categories:

1. **PRAGMA statements** - PostgreSQL doesn't support SQLite PRAGMA directives
2. **Missing UNIQUE constraints** - PostgreSQL schema lacks constraints present in SQLite
3. **Single-quoted string literals in SQL** - SQL injection vulnerabilities
4. **GROUP BY strictness** - PostgreSQL requires all non-aggregated columns in GROUP BY
5. **ROWID dependency** - PostgreSQL doesn't have implicit ROWID
6. **STRFTIME function** - PostgreSQL uses different date formatting functions
7. **String concatenation in queries** - SQL injection vulnerabilities in IN clauses

**Impact:** Application will fail to start or crash during runtime when using PostgreSQL backend.

**Priority:** CRITICAL - These issues prevent basic PostgreSQL functionality.

---

## Complete Fix List

### Issue 1: PRAGMA Statement (Line 62)

**Location:** Line 62 in `createSchemaQueries`

**Problem:** PostgreSQL doesn't support SQLite's PRAGMA statements.

**Current Code:**
```python
createSchemaQueries = [
    "PRAGMA journal_mode=WAL",
    "CREATE TABLE tbl_event_types ( \
```

**Fixed Code:**
```python
createSchemaQueries = [
    # PRAGMA removed - not supported in PostgreSQL, only used for SQLite
    "CREATE TABLE tbl_event_types ( \
```

**Alternative Fix:** Conditionally execute based on db_type
```python
if self.db_type == 'sqlite':
    self.dbh.execute("PRAGMA journal_mode=WAL")
```

---

### Issue 2: Missing UNIQUE Constraint on tbl_scan_config (Line 170)

**Location:** Line 170 in `createPostgreSQLSchemaQueries`

**Problem:** PostgreSQL schema missing UNIQUE constraint that exists in SQLite version (line 96).

**Current Code (Line 165-170):**
```python
"CREATE TABLE IF NOT EXISTS tbl_scan_config ( \
    scan_instance_id    VARCHAR NOT NULL REFERENCES tbl_scan_instance(guid), \
    component           VARCHAR NOT NULL, \
    opt                 VARCHAR NOT NULL, \
    val                 VARCHAR NOT NULL \
)",
```

**Fixed Code:**
```python
"CREATE TABLE IF NOT EXISTS tbl_scan_config ( \
    scan_instance_id    VARCHAR NOT NULL REFERENCES tbl_scan_instance(guid), \
    component           VARCHAR NOT NULL, \
    opt                 VARCHAR NOT NULL, \
    val                 VARCHAR NOT NULL, \
    UNIQUE (scan_instance_id, component, opt) \
)",
```

**Impact:** Prevents duplicate configuration entries and maintains data integrity.

---

### Issue 3: Missing UNIQUE Constraint on tbl_scan_results.hash (Line 173)

**Location:** Line 173 in `createPostgreSQLSchemaQueries`

**Problem:** The `hash` column has UNIQUE constraint on line 173 but it's already correct. This is actually properly implemented.

**Current Code (Line 173):**
```python
hash                VARCHAR NOT NULL UNIQUE,
```

**Status:** ✅ **Already Fixed** - No action needed.

---

### Issue 4: SQL Injection - String Concatenation (Line 687)

**Location:** Line 687 in `search()` method

**Problem:** Uses single-quoted alias in SELECT which can cause issues and is non-standard.

**Current Code (Line 683-687):**
```python
qry = "SELECT ROUND(c.generated) AS generated, c.data, \
    s.data as source_data, \
    c.module, c.type, c.confidence, c.visibility, c.risk, c.hash, \
    c.source_event_hash, t.event_descr, t.event_type, c.scan_instance_id, \
    c.false_positive as fp, s.false_positive as parent_fp \
```

**Fixed Code:**
```python
qry = "SELECT ROUND(c.generated) AS generated, c.data, \
    s.data AS source_data, \
    c.module, c.type, c.confidence, c.visibility, c.risk, c.hash, \
    c.source_event_hash, t.event_descr, t.event_type, c.scan_instance_id, \
    c.false_positive AS fp, s.false_positive AS parent_fp \
```

**Change:** Lowercase `as` → Uppercase `AS` for consistency and standards compliance.

---

### Issue 5: GROUP BY Missing Columns (Lines 1084-1086)

**Location:** Line 1084-1086 in `scanCorrelationSummary()` method

**Problem:** PostgreSQL requires `rule_id` in GROUP BY clause when used in SELECT.

**Current Code:**
```python
if by == "risk":
    qry = f"SELECT rule_risk, count(*) AS total FROM \
        tbl_scan_correlation_results \
        WHERE scan_instance_id = {ph} GROUP BY rule_risk, rule_id ORDER BY rule_id"
```

**Fixed Code:**
```python
if by == "risk":
    qry = f"SELECT rule_risk, rule_id, count(*) AS total FROM \
        tbl_scan_correlation_results \
        WHERE scan_instance_id = {ph} GROUP BY rule_risk, rule_id ORDER BY rule_id"
```

**Change:** Added `rule_id` to SELECT clause to match GROUP BY and ORDER BY.

---

### Issue 6: GROUP BY Missing Columns (Lines 1089-1092)

**Location:** Lines 1089-1092 in `scanCorrelationSummary()` method

**Problem:** Already correctly includes all columns in GROUP BY. ✅ No fix needed.

**Current Code:**
```python
if by == "rule":
    qry = f"SELECT rule_id, rule_name, rule_risk, rule_descr, \
        count(*) AS total FROM \
        tbl_scan_correlation_results \
        WHERE scan_instance_id = {ph} GROUP BY rule_id, rule_name, rule_risk, rule_descr ORDER BY rule_id"
```

**Status:** ✅ **Already Correct** - No action needed.

---

### Issue 7: GROUP BY Missing Columns (Lines 1123-1127)

**Location:** Lines 1123-1127 in `scanCorrelationList()` method

**Problem:** PostgreSQL requires all non-aggregated SELECT columns in GROUP BY.

**Current Code:**
```python
qry = f"SELECT c.id, c.title, c.rule_id, c.rule_risk, c.rule_name, \
    c.rule_descr, c.rule_logic, count(e.event_hash) AS event_count FROM \
    tbl_scan_correlation_results c, tbl_scan_correlation_results_events e \
    WHERE scan_instance_id = {ph} AND c.id = e.correlation_id \
    GROUP BY c.id ORDER BY c.title, c.rule_risk"
```

**Fixed Code:**
```python
qry = f"SELECT c.id, c.title, c.rule_id, c.rule_risk, c.rule_name, \
    c.rule_descr, c.rule_logic, count(e.event_hash) AS event_count FROM \
    tbl_scan_correlation_results c, tbl_scan_correlation_results_events e \
    WHERE scan_instance_id = {ph} AND c.id = e.correlation_id \
    GROUP BY c.id, c.title, c.rule_id, c.rule_risk, c.rule_name, c.rule_descr, c.rule_logic \
    ORDER BY c.title, c.rule_risk"
```

**Change:** Added `c.title, c.rule_id, c.rule_risk, c.rule_name, c.rule_descr, c.rule_logic` to GROUP BY.

---

### Issue 8: ROWID Dependency (Line 1309)

**Location:** Line 1309 in `scanLogs()` method

**Problem:** PostgreSQL doesn't have implicit `rowid` column. Need to use PostgreSQL's OID or add explicit column.

**Current Code (Lines 1309-1310):**
```python
qry = f"SELECT generated AS generated, component, \
    type, message, rowid FROM tbl_scan_log WHERE scan_instance_id = {ph}"
```

**Fixed Code - Option 1 (Use ctid - PostgreSQL internal):**
```python
if self.db_type == 'sqlite':
    qry = f"SELECT generated AS generated, component, \
        type, message, rowid FROM tbl_scan_log WHERE scan_instance_id = {ph}"
else:  # postgresql
    qry = f"SELECT generated AS generated, component, \
        type, message, ctid::text::bigint FROM tbl_scan_log WHERE scan_instance_id = {ph}"
```

**Fixed Code - Option 2 (Add ID column to schema - RECOMMENDED):**

Add to PostgreSQL schema (after line 164):
```python
"CREATE TABLE IF NOT EXISTS tbl_scan_log ( \
    id                  SERIAL PRIMARY KEY, \
    scan_instance_id    VARCHAR NOT NULL REFERENCES tbl_scan_instance(guid), \
    generated           BIGINT NOT NULL, \
    component           VARCHAR, \
    type                VARCHAR NOT NULL, \
    message             VARCHAR \
)",
```

Then update query (line 1309):
```python
if self.db_type == 'sqlite':
    qry = f"SELECT generated AS generated, component, \
        type, message, rowid FROM tbl_scan_log WHERE scan_instance_id = {ph}"
else:  # postgresql
    qry = f"SELECT generated AS generated, component, \
        type, message, id FROM tbl_scan_log WHERE scan_instance_id = {ph}"
```

**Recommended:** Option 2 - More reliable and explicit.

---

### Issue 9: GROUP BY with Integer Literal (Lines 1773-1782)

**Location:** Lines 1773-1782 in `scanInstanceList()` method

**Problem:** Multiple issues:
- Uses string literal `'0'` in SELECT (should be integer 0)
- Missing columns in GROUP BY clause
- Uses non-standard integer literals in GROUP BY for PostgreSQL

**Current Code:**
```python
qry = "SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000), \
    ROUND(i.started)/1000 as started, ROUND(i.ended)/1000, i.status, COUNT(r.type) \
    FROM tbl_scan_instance i, tbl_scan_results r WHERE i.guid = r.scan_instance_id \
    AND r.type <> 'ROOT' GROUP BY i.guid \
    UNION ALL \
    SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000), \
    ROUND(i.started)/1000 as started, ROUND(i.ended)/1000, i.status, '0' \
    FROM tbl_scan_instance i  WHERE i.guid NOT IN ( \
    SELECT distinct scan_instance_id FROM tbl_scan_results WHERE type <> 'ROOT') \
    ORDER BY started DESC"
```

**Fixed Code:**
```python
qry = "SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000) AS created, \
    ROUND(i.started)/1000 AS started, ROUND(i.ended)/1000 AS ended, i.status, COUNT(r.type) \
    FROM tbl_scan_instance i, tbl_scan_results r WHERE i.guid = r.scan_instance_id \
    AND r.type <> 'ROOT' GROUP BY i.guid, i.name, i.seed_target, i.created, i.started, i.ended, i.status \
    UNION ALL \
    SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000) AS created, \
    ROUND(i.started)/1000 AS started, ROUND(i.ended)/1000 AS ended, i.status, 0 \
    FROM tbl_scan_instance i  WHERE i.guid NOT IN ( \
    SELECT DISTINCT scan_instance_id FROM tbl_scan_results WHERE type <> 'ROOT') \
    ORDER BY started DESC"
```

**Changes:**
- Added explicit `AS` aliases for all computed columns
- Changed `'0'` (string) to `0` (integer)
- Added all non-aggregated columns to first GROUP BY: `i.name, i.seed_target, i.created, i.started, i.ended, i.status`
- Changed `distinct` to `DISTINCT` (uppercase for consistency)

---

### Issue 10: STRFTIME Function (Line 1811)

**Location:** Line 1811 in `scanResultHistory()` method

**Problem:** PostgreSQL doesn't support SQLite's STRFTIME function. Must use TO_CHAR or equivalent.

**Current Code:**
```python
qry = f"SELECT STRFTIME('%H:%M %w', generated, 'unixepoch') AS hourmin, \
        type, COUNT(*) FROM tbl_scan_results \
        WHERE scan_instance_id = {ph} GROUP BY hourmin, type"
```

**Fixed Code:**
```python
if self.db_type == 'sqlite':
    qry = f"SELECT STRFTIME('%H:%M %w', generated, 'unixepoch') AS hourmin, \
            type, COUNT(*) FROM tbl_scan_results \
            WHERE scan_instance_id = {ph} GROUP BY hourmin, type"
else:  # postgresql
    qry = f"SELECT TO_CHAR(TO_TIMESTAMP(generated/1000), 'HH24:MI D') AS hourmin, \
            type, COUNT(*) FROM tbl_scan_results \
            WHERE scan_instance_id = {ph} GROUP BY hourmin, type"
```

**Notes:**
- SQLite `generated` is in milliseconds, treating as Unix epoch
- PostgreSQL TO_TIMESTAMP expects seconds, so divide by 1000
- `%H:%M` → `HH24:MI` (24-hour format, minutes)
- `%w` → `D` (day of week, 1-7)

---

### Issue 11: SQL Injection in IN Clause (Line 1868)

**Location:** Line 1868 in `scanElementSourcesDirect()` method

**Problem:** SQL injection vulnerability - directly concatenating unsanitized hashIds into query.

**Current Code:**
```python
hashIds = []
for hashId in elementIdList:
    if not hashId:
        continue
    if not hashId.isalnum():
        continue
    hashIds.append(hashId)

# ...
qry = f"SELECT ROUND(c.generated) AS generated, c.data, \
    s.data as source_data, \
    c.module, c.type, c.confidence, c.visibility, c.risk, c.hash, \
    c.source_event_hash, t.event_descr, t.event_type, s.scan_instance_id, \
    c.false_positive as fp, s.false_positive as parent_fp, \
    s.type, s.module, st.event_type as source_entity_type \
    FROM tbl_scan_results c, tbl_scan_results s, tbl_event_types t, \
    tbl_event_types st \
    WHERE c.scan_instance_id = {ph} AND c.source_event_hash = s.hash AND \
    s.scan_instance_id = c.scan_instance_id AND st.event = s.type AND \
    t.event = c.type AND c.hash in ('%s')" % "','".join(hashIds)
qvars = [instanceId]
```

**Fixed Code:**
```python
hashIds = []
for hashId in elementIdList:
    if not hashId:
        continue
    if not hashId.isalnum():
        continue
    hashIds.append(hashId)

# Build parameterized query
ph = self._placeholder()
hash_placeholders = ", ".join([ph] * len(hashIds))

qry = f"SELECT ROUND(c.generated) AS generated, c.data, \
    s.data AS source_data, \
    c.module, c.type, c.confidence, c.visibility, c.risk, c.hash, \
    c.source_event_hash, t.event_descr, t.event_type, s.scan_instance_id, \
    c.false_positive AS fp, s.false_positive AS parent_fp, \
    s.type, s.module, st.event_type AS source_entity_type \
    FROM tbl_scan_results c, tbl_scan_results s, tbl_event_types t, \
    tbl_event_types st \
    WHERE c.scan_instance_id = {ph} AND c.source_event_hash = s.hash AND \
    s.scan_instance_id = c.scan_instance_id AND st.event = s.type AND \
    t.event = c.type AND c.hash IN ({hash_placeholders})"
qvars = [instanceId] + hashIds
```

**Changes:**
- Generate proper placeholders using `_placeholder()` method
- Build IN clause with parameterized placeholders
- Extend qvars with hashIds list
- Changed `as` to `AS` for consistency

---

### Issue 12: SQL Injection in IN Clause (Line 1921)

**Location:** Line 1921 in `scanElementChildrenDirect()` method

**Problem:** Same SQL injection vulnerability as Issue 11.

**Current Code:**
```python
hashIds = []
for hashId in elementIdList:
    if not hashId:
        continue
    if not hashId.isalnum():
        continue
    hashIds.append(hashId)

# ...
qry = f"SELECT ROUND(c.generated) AS generated, c.data, \
    s.data as source_data, \
    c.module, c.type, c.confidence, c.visibility, c.risk, c.hash, \
    c.source_event_hash, t.event_descr, t.event_type, s.scan_instance_id, \
    c.false_positive as fp, s.false_positive as parent_fp \
    FROM tbl_scan_results c, tbl_scan_results s, tbl_event_types t \
    WHERE c.scan_instance_id = {ph} AND c.source_event_hash = s.hash AND \
    s.scan_instance_id = c.scan_instance_id AND \
    t.event = c.type AND s.hash in ('%s')" % "','".join(hashIds)
qvars = [instanceId]
```

**Fixed Code:**
```python
hashIds = []
for hashId in elementIdList:
    if not hashId:
        continue
    if not hashId.isalnum():
        continue
    hashIds.append(hashId)

# Build parameterized query
ph = self._placeholder()
hash_placeholders = ", ".join([ph] * len(hashIds))

qry = f"SELECT ROUND(c.generated) AS generated, c.data, \
    s.data AS source_data, \
    c.module, c.type, c.confidence, c.visibility, c.risk, c.hash, \
    c.source_event_hash, t.event_descr, t.event_type, s.scan_instance_id, \
    c.false_positive AS fp, s.false_positive AS parent_fp \
    FROM tbl_scan_results c, tbl_scan_results s, tbl_event_types t \
    WHERE c.scan_instance_id = {ph} AND c.source_event_hash = s.hash AND \
    s.scan_instance_id = c.scan_instance_id AND \
    t.event = c.type AND s.hash IN ({hash_placeholders})"
qvars = [instanceId] + hashIds
```

**Changes:**
- Generate proper placeholders using `_placeholder()` method
- Build IN clause with parameterized placeholders
- Extend qvars with hashIds list
- Changed `as` to `AS` for consistency

---

## Quick Reference Summary

| Line(s) | Issue | Priority | Fix Type |
|---------|-------|----------|----------|
| 62 | PRAGMA statement | HIGH | Remove or conditionally execute |
| 170 | Missing UNIQUE constraint | MEDIUM | Add UNIQUE constraint |
| 687 | Lowercase 'as' alias | LOW | Change to uppercase AS |
| 1084-1086 | Missing column in SELECT | HIGH | Add rule_id to SELECT |
| 1123-1127 | GROUP BY missing columns | HIGH | Add all SELECT columns to GROUP BY |
| 1309 | ROWID dependency | CRITICAL | Add ID column or use ctid |
| 1773-1782 | GROUP BY + literal issues | HIGH | Fix GROUP BY, change '0' to 0, add AS |
| 1811 | STRFTIME function | HIGH | Replace with TO_CHAR for PostgreSQL |
| 1868 | SQL injection (IN clause) | CRITICAL | Use parameterized query |
| 1921 | SQL injection (IN clause) | CRITICAL | Use parameterized query |

---

## Testing Checklist

After applying ALL fixes, test the following functionality:

### 1. Database Initialization
- [ ] PostgreSQL database schema creation succeeds
- [ ] All tables created with correct constraints
- [ ] All indexes created successfully
- [ ] Event types populated correctly

### 2. Core Operations
- [ ] Scan instance creation
- [ ] Scan configuration storage
- [ ] Event storage and retrieval
- [ ] Scan logging functionality

### 3. Search & Queries
- [ ] Search functionality (search() method)
- [ ] Scan result summaries by type/module/entity
- [ ] Correlation summaries and lists
- [ ] Scan logs retrieval with pagination

### 4. History & Navigation
- [ ] Scan instance listing
- [ ] Scan result history (time-based)
- [ ] Element source/children navigation
- [ ] Correlation results

### 5. SQL Injection Testing
- [ ] Test IN clauses with special characters
- [ ] Verify parameterized queries work
- [ ] No SQL errors with edge case inputs

### 6. Performance
- [ ] GROUP BY queries execute efficiently
- [ ] Index usage verified with EXPLAIN
- [ ] No full table scans on large datasets

---

## Rollback Instructions

### If Issues Occur After Applying Fixes:

1. **Immediate Rollback**
   ```bash
   cd /stuff/spiderfoot/spiderfoot
   git checkout HEAD -- db.py
   ```

2. **Partial Rollback** (if only specific fixes cause issues)
   - Identify the problematic fix from git diff
   - Manually revert that specific change
   - Keep other fixes in place

3. **Database Schema Rollback**
   ```bash
   # For PostgreSQL - drop and recreate
   psql -U spiderfoot_user -d spiderfoot_db
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   \q
   ```

4. **Restore from Backup**
   ```bash
   # If you backed up before changes
   pg_restore -U spiderfoot_user -d spiderfoot_db /path/to/backup.sql
   ```

### Rollback Decision Tree:

```
Does app start successfully?
├─ NO → Full rollback (Step 1)
├─ YES →
    └─ Do queries execute?
        ├─ NO → Check query-specific fixes (Issues 5-12)
        ├─ YES →
            └─ Are results correct?
                ├─ NO → Check data transformation (Issue 10, STRFTIME)
                └─ YES → Success!
```

---

## Prevention & Best Practices

### For Future Development:

1. **Always Use Parameterized Queries**
   - Never concatenate user input into SQL
   - Use `_placeholder()` method for all variables
   - Extend qvars list properly

2. **Database Compatibility**
   - Test on both SQLite and PostgreSQL
   - Use conditional logic for DB-specific features
   - Follow SQL standards (ANSI SQL)

3. **GROUP BY Rules**
   - Include ALL non-aggregated SELECT columns
   - PostgreSQL is stricter than SQLite
   - Use explicit column names, not positions

4. **Date/Time Functions**
   - Abstract into helper methods
   - Support both database types
   - Document timestamp formats

5. **Schema Management**
   - Keep SQLite and PostgreSQL schemas in sync
   - Document any differences
   - Test migrations on both platforms

---

## Implementation Order (Recommended)

Apply fixes in this order to minimize risk:

1. **Phase 1: Critical Security Fixes**
   - Issue 11 (Line 1868) - SQL Injection
   - Issue 12 (Line 1921) - SQL Injection

2. **Phase 2: Schema Fixes**
   - Issue 1 (Line 62) - PRAGMA
   - Issue 2 (Line 170) - UNIQUE constraint
   - Issue 8 (Line 1309) - ROWID (requires schema change)

3. **Phase 3: Query Fixes**
   - Issue 5 (Lines 1084-1086) - GROUP BY
   - Issue 7 (Lines 1123-1127) - GROUP BY
   - Issue 9 (Lines 1773-1782) - GROUP BY + literals

4. **Phase 4: Function Compatibility**
   - Issue 10 (Line 1811) - STRFTIME

5. **Phase 5: Style/Standards**
   - Issue 4 (Line 687) - Alias case

**Test after each phase** before proceeding to the next.

---

## Additional Notes

### Database Type Detection
The code uses `self.db_type` to detect database type. Ensure this is set correctly:
- SQLite: `self.db_type == 'sqlite'`
- PostgreSQL: `self.db_type == 'postgresql'`

### Placeholder Method
The `_placeholder()` method returns appropriate placeholders:
- SQLite: `?`
- PostgreSQL: `%s`

Always use this method instead of hardcoding placeholders.

### Transaction Management
Both databases use similar transaction patterns:
- `self.conn.commit()` - Commit changes
- `self.conn.rollback()` - Rollback on error

### Error Handling
Catch both database-specific errors:
```python
except (sqlite3.Error, psycopg2.Error if psycopg2 else Exception) as e:
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-06 | Initial comprehensive fix document |

---

## Contact & Support

For issues or questions about these fixes:
1. Check SpiderFoot GitHub Issues
2. Review PostgreSQL compatibility documentation
3. Test thoroughly in development environment before production

---

**End of Document**
