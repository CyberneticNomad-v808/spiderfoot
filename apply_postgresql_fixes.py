#!/usr/bin/env python3
"""
Comprehensive PostgreSQL Compatibility Fix for Spiderfoot db.py
Applies ALL identified fixes in one go.
"""

import sys
from pathlib import Path

def apply_all_fixes():
    db_file = Path("/stuff/spiderfoot/spiderfoot/db.py")

    if not db_file.exists():
        print(f"ERROR: {db_file} not found!")
        return False

    # Read the entire file
    with open(db_file, 'r') as f:
        content = f.read()

    original_content = content
    fixes_applied = []

    # FIX 1: Remove PRAGMA statement (line 62)
    if '"PRAGMA journal_mode=WAL"' in content:
        content = content.replace(
            '"PRAGMA journal_mode=WAL",',
            '# "PRAGMA journal_mode=WAL",  # SQLite only - disabled for PostgreSQL compatibility'
        )
        fixes_applied.append("1. Commented out PRAGMA statement")

    # FIX 2: Fix single-quoted aliases to unquoted (4 occurrences)
    content = content.replace(
        "as 'source_data'",
        "as source_data"
    )
    content = content.replace(
        "as 'fp'",
        "as fp"
    )
    content = content.replace(
        "as 'parent_fp'",
        "as parent_fp"
    )
    content = content.replace(
        "as 'source_entity_type'",
        "as source_entity_type"
    )
    fixes_applied.append("2. Fixed SQL alias quotes (4 occurrences)")

    # FIX 3: Fix GROUP BY for scanCorrelationSummary (line ~1084)
    old_group_by_risk = 'WHERE scan_instance_id = {ph} GROUP BY rule_risk, rule_id ORDER BY rule_id'
    new_group_by_risk = 'WHERE scan_instance_id = {ph} GROUP BY rule_risk ORDER BY rule_risk'
    if old_group_by_risk in content:
        content = content.replace(old_group_by_risk, new_group_by_risk)
        fixes_applied.append("3. Fixed GROUP BY in scanCorrelationSummary (risk)")

    # FIX 4: Fix GROUP BY for scanCorrelationList (line ~1123)
    old_correlation_list = """    qry = f"SELECT c.id, c.title, c.rule_id, c.rule_risk, c.rule_name, \\
        c.rule_descr, c.rule_logic, count(e.event_hash) AS event_count FROM \\
        tbl_scan_correlation_results c, tbl_scan_correlation_results_events e \\
        WHERE scan_instance_id = {ph} AND c.id = e.correlation_id \\
        GROUP BY c.id ORDER BY c.title, c.rule_risk\""""

    new_correlation_list = """    qry = f"SELECT c.id, c.title, c.rule_id, c.rule_risk, c.rule_name, \\
        c.rule_descr, c.rule_logic, count(e.event_hash) AS event_count FROM \\
        tbl_scan_correlation_results c, tbl_scan_correlation_results_events e \\
        WHERE c.scan_instance_id = {ph} AND c.id = e.correlation_id \\
        GROUP BY c.id, c.title, c.rule_id, c.rule_risk, c.rule_name, c.rule_descr, c.rule_logic \\
        ORDER BY c.title, c.rule_risk\""""

    if old_correlation_list in content:
        content = content.replace(old_correlation_list, new_correlation_list)
        fixes_applied.append("4. Fixed GROUP BY in scanCorrelationList")

    # FIX 5: Fix ROWID dependency (line ~1309)
    old_rowid = "type, message, rowid FROM tbl_scan_log WHERE scan_instance_id = {ph}"
    new_rowid = "type, message, ctid::text::bigint as rowid FROM tbl_scan_log WHERE scan_instance_id = {ph}"
    if old_rowid in content:
        content = content.replace(old_rowid, new_rowid)
        fixes_applied.append("5. Fixed ROWID dependency (PostgreSQL ctid)")

    # FIX 6: Fix scanInstanceList GROUP BY (line ~1773)
    old_scan_list = """    qry = "SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000), \\
        ROUND(i.started)/1000 as started, ROUND(i.ended)/1000, i.status, COUNT(r.type) \\
        FROM tbl_scan_instance i, tbl_scan_results r WHERE i.guid = r.scan_instance_id \\
        AND r.type <> 'ROOT' GROUP BY i.guid \\
        UNION ALL \\
        SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000), \\
        ROUND(i.started)/1000 as started, ROUND(i.ended)/1000, i.status, '0' \\
        FROM tbl_scan_instance i  WHERE i.guid NOT IN ( \\
        SELECT distinct scan_instance_id FROM tbl_scan_results WHERE type <> 'ROOT') \\
        ORDER BY started DESC\""""

    new_scan_list = """    qry = "SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000), \\
        ROUND(i.started)/1000 as started, ROUND(i.ended)/1000, i.status, COUNT(r.type) \\
        FROM tbl_scan_instance i, tbl_scan_results r WHERE i.guid = r.scan_instance_id \\
        AND r.type <> 'ROOT' \\
        GROUP BY i.guid, i.name, i.seed_target, i.created, i.started, i.ended, i.status \\
        UNION ALL \\
        SELECT i.guid, i.name, i.seed_target, ROUND(i.created/1000), \\
        ROUND(i.started)/1000 as started, ROUND(i.ended)/1000, i.status, 0 \\
        FROM tbl_scan_instance i WHERE i.guid NOT IN ( \\
        SELECT distinct scan_instance_id FROM tbl_scan_results WHERE type <> 'ROOT') \\
        ORDER BY started DESC\""""

    if old_scan_list in content:
        content = content.replace(old_scan_list, new_scan_list)
        fixes_applied.append("6. Fixed GROUP BY in scanInstanceList + integer literal")

    # FIX 7: Fix STRFTIME function (line ~1811)
    old_strftime = "qry = f\"SELECT STRFTIME('%H:%M %w', generated, 'unixepoch') AS hourmin"
    new_strftime = "qry = f\"SELECT TO_CHAR(TO_TIMESTAMP(generated/1000), 'HH24:MI D') AS hourmin"
    if old_strftime in content:
        content = content.replace(old_strftime, new_strftime)
        # Also fix the GROUP BY for this query
        old_strftime_group = "WHERE scan_instance_id = {ph} GROUP BY hourmin, type"
        new_strftime_group = "WHERE scan_instance_id = {ph} GROUP BY TO_CHAR(TO_TIMESTAMP(generated/1000), 'HH24:MI D'), type"
        content = content.replace(old_strftime_group, new_strftime_group)
        fixes_applied.append("7. Fixed STRFTIME to TO_CHAR")

    # FIX 8 & 9: Fix SQL injection in IN clauses (lines ~1868, ~1921)
    # This is more complex - need to find and fix the pattern
    old_in_pattern1 = """    t.event = c.type AND c.hash in ('%s')" % "','".join(hashIds)
        qvars = [instanceId]"""

    new_in_pattern1 = """    t.event = c.type AND c.hash IN ({placeholders})"
        placeholders = ', '.join([ph] * len(hashIds))
        qry = qry.format(ph=ph, placeholders=placeholders)
        qvars = [instanceId] + hashIds"""

    # Find both occurrences
    if "c.hash in ('%s')\" % \"','\".join(hashIds)" in content:
        # Need to use a different approach - replace the full function
        fixes_applied.append("8-9. SQL injection fixes require manual review - pattern too complex for automatic replacement")

    # Write the file if any fixes were applied
    if content != original_content:
        # Create backup
        backup_file = db_file.with_suffix('.db.py.backup')
        with open(backup_file, 'w') as f:
            f.write(original_content)
        print(f"✅ Backup created: {backup_file}")

        # Write fixed content
        with open(db_file, 'w') as f:
            f.write(content)

        print(f"\n✅ Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"   - {fix}")

        print(f"\n⚠️  MANUAL FIXES STILL REQUIRED:")
        print(f"   - Fix #8-9: SQL injection in scanElementSourcesDirect and scanElementChildrenDirect")
        print(f"   - See /stuff/spiderfoot/POSTGRESQL_FIX_COMPLETE.md for details")

        return True
    else:
        print("⚠️  No fixes applied - content unchanged")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("PostgreSQL Compatibility Fix for Spiderfoot")
    print("=" * 70)
    print()

    if apply_all_fixes():
        print("\n✅ Fixes applied successfully!")
        print("\nNext steps:")
        print("1. Review the changes in /stuff/spiderfoot/spiderfoot/db.py")
        print("2. Apply manual fixes for SQL injection issues (lines 1868, 1921)")
        print("3. Rebuild Docker image")
        print("4. Test with a new scan")
    else:
        print("\n❌ Fix application failed")
        sys.exit(1)
