---
description: Validate spec documentation against current codebase and tests, check regression test health
---

# Spec Validation Command

Validate that spec documentation remains accurate and check regression test health.

## Instructions

You are a specification validation specialist. When the user runs `/spec-validate [feature-name]`:

### 1. If No Feature Name Provided

**Validate ALL specs in `/stuff/coding_standards/spiderfoot-as-is-documentation/`:**

1. **Find All Specs**
   - List all spec directories in `/stuff/coding_standards/spiderfoot-as-is-documentation/`
   - For each spec, identify key files (requirements, design docs, regression registry)

2. **Run Quick Health Check**
   - Count total specs
   - Check last modified dates
   - Identify any missing key files

3. **Check Regression Test Health**
   - Read `/stuff/coding_standards/spiderfoot-as-is-documentation/regressions/REGISTRY.md` files
   - List all tracked regressions
   - Check status of each regression
   - Identify regressions without tests

4. **Report Summary**
```
📊 Spec Validation Summary

**Specs Found:** [count]
**Last Updated:** [dates]

**Regression Health:**
- Total Regressions: [count]
- With Tests: [count] ([%])
- Active Monitoring: [count]
- Need Tests: [count]

**Action Items:**
- [ ] [Any issues found]

Run `/spec-validate [feature-name]` for detailed validation.
```

---

### 2. If Feature Name Provided

**Validate specific spec deeply:**

#### A. Validate File References

1. **Extract All File References**
   - Read all spec documents for the feature
   - Find all file path references (e.g., `test/unit/test_foo.py`)
   - Find all code references (e.g., `spiderfoot/db/__init__.py:123`)

2. **Check Files Exist**
   - Use Bash to verify each referenced file exists
   - Report missing files
   - Note moved/renamed files

3. **Check Line Number Accuracy** (sample check)
   - For critical references, read the file
   - Verify content at referenced line numbers is relevant
   - Flag if content has significantly changed

#### B. Validate Test References

1. **Find All Test References**
   - Extract test file paths from specs
   - Extract test function names
   - Extract line number ranges

2. **Verify Tests Exist**
   - Check each test file exists
   - Search for test function names in files
   - Report missing tests

3. **Check Test Status** (optional, if quick)
   - Try running a sample of referenced tests
   - Report pass/fail status
   - Flag if tests are skipped/disabled

#### C. Validate Traceability

1. **Check Requirement Links**
   - Find all REQ-*, UR-*, SR-*, NFR-* references
   - Verify requirements exist in requirements docs
   - Check bidirectional links

2. **Check Specification Links**
   - Find all SPEC-* references
   - Verify specifications exist in design docs
   - Check consistency

3. **Check Test-to-Spec Links**
   - Verify each spec has at least one test reference
   - Verify each test reference has a spec
   - Report orphaned items

#### D. Validate Regression Health

1. **Check Regression Registry**
   - Read `/stuff/coding_standards/spiderfoot-as-is-documentation/regressions/REGISTRY.md`
   - List all regressions (REG-*)
   - Check each regression entry file exists

2. **Validate Regression Entries**
   - For each REG-* entry:
     - Check traceability links (to REQ, SPEC, tests)
     - Verify test files exist
     - Check status (Open/Fixed/Monitoring)
     - Verify "Fixed" regressions have tests

3. **Check Regression Test Files**
   - Find all test files in `test/regression/`
   - Check if they're referenced in registry
   - Report orphaned regression tests
   - Report regressions without tests

4. **Run Regression Tests** (if requested)
   - Identify regression test files
   - Optionally run them with pytest
   - Report pass/fail status

#### E. Check for Documentation Drift

1. **Check Last Modified Dates**
   - Compare spec file dates to source code dates
   - Flag if source changed recently but spec didn't
   - Suggest specs that may need review

2. **Check for New Code**
   - Search for new test files not referenced in specs
   - Search for new modules not documented
   - Suggest specs that may need updates

3. **Check for Deprecated References**
   - Look for "TODO", "FIXME", "DEPRECATED" in specs
   - Flag outdated information
   - Suggest cleanup

---

## Output Format

### Detailed Validation Report

```markdown
# Spec Validation Report: [feature-name]

**Date:** [timestamp]
**Spec Location:** `/stuff/coding_standards/spiderfoot-as-is-documentation/`
**Status:** ✅ Healthy / ⚠️ Needs Attention / ❌ Issues Found

---

## File Reference Validation

**Total References:** [count]
**Valid:** [count] ✅
**Missing:** [count] ❌
**Moved/Renamed:** [count] ⚠️

### Missing Files
- ❌ `[file path]` - Referenced in [spec file:line]

### Suspicious References
- ⚠️ `[file:line]` - Content may have changed

---

## Test Reference Validation

**Total Test References:** [count]
**Valid Tests:** [count] ✅
**Missing Tests:** [count] ❌
**Test Functions:** [count]

### Missing Tests
- ❌ `[test file]` - Referenced in [spec file]
- ❌ `[test function]` - Expected in [test file]

---

## Traceability Validation

**Requirements:** [count found] / [count referenced]
**Specifications:** [count found] / [count referenced]
**Bidirectional Links:** [valid/total]

### Broken Links
- ❌ REQ-XXX-### - Referenced but not found
- ❌ SPEC-XXX-### - Referenced but not found

### Orphaned Items
- ⚠️ [item] - Has no forward/backward link

---

## Regression Health Check

**Total Regressions:** [count]
**With Tests:** [count] ([%]) ✅
**Without Tests:** [count] ([%]) ❌
**Active Monitoring:** [count]
**Regression Test Status:** ✅ Passing / ❌ Failing / ⏳ Not Run

### Regressions

| ID | Title | Status | Tests | Test Status |
|---|---|---|---|---|
| REG-001 | [Title] | Fixed | ✅ 15 tests | ✅ Passing |
| REG-002 | [Title] | Open | ❌ No tests | ⏳ N/A |

### Regressions Needing Tests
- ❌ REG-XXX: [Title] - No regression tests found

### Regression Test Files

**Referenced in Registry:** [count]
**Found in test/regression/:** [count]

**Orphaned Test Files:**
- ⚠️ `test/regression/test_foo.py` - Not referenced in registry

---

## Documentation Drift Check

**Spec Last Updated:** [date]
**Code Last Updated:** [date]
**Drift:** [days] days

### Recently Changed Code (Not in Specs)
- ⚠️ `[file]` - Modified [date], spec updated [date]

### New Tests (Not in Specs)
- ⚠️ `[test file]` - Created [date], not documented

---

## Recommendations

### Immediate Actions
- [ ] Fix missing file references
- [ ] Create missing regression tests
- [ ] Update outdated traceability links

### Maintenance Actions
- [ ] Review specs for drift (code changed recently)
- [ ] Document new tests
- [ ] Update regression registry

### Health Score: [X/100]

**Scoring:**
- File references valid: [score]/30
- Test references valid: [score]/25
- Traceability complete: [score]/20
- Regression coverage: [score]/15
- Documentation currency: [score]/10

---

**Validation Complete**
**Next Validation:** [Recommended date]
```

---

## Validation Thoroughness

### Quick Validation
- Check file existence only
- Count references
- Report obvious issues
- ~1-2 minutes

### Standard Validation (Default)
- Check files and test references
- Validate traceability
- Check regression health
- ~3-5 minutes

### Deep Validation (use `--deep` flag)
- Run regression tests
- Check line number accuracy
- Search for drift
- Validate all links
- ~10+ minutes

---

## Usage Examples

```bash
# Validate all specs (quick overview)
/spec-validate

# Validate specific spec (standard)
/spec-validate spiderfoot-as-is

# Deep validation with test execution
/spec-validate spiderfoot-as-is --deep

# Just check regression health
/spec-validate spiderfoot-as-is --regressions-only
```

---

## Automation Integration

**Suggested Schedule:**
- **Daily:** Quick validation (file existence)
- **Weekly:** Standard validation (full traceability)
- **Before Release:** Deep validation (run all tests)
- **After Major Changes:** Immediate validation

**CI/CD Integration:**
Run as part of pull request checks to ensure specs stay current.

---

## Important Notes

- Always report specific file paths and line numbers
- Provide actionable recommendations
- Prioritize critical issues (missing tests, broken traceability)
- Consider validation speed vs thoroughness
- Update REGISTRY.md with validation date
- Create GitHub issues for significant drift

---

## Error Handling

If validation cannot complete:
- Report partial results
- Explain what failed
- Suggest manual verification steps
- Note issues in validation log
