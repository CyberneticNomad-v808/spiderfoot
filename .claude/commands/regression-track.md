---
description: Track a new regression with automatic traceability to specs, requirements, and tests
---

# Regression Tracking Command

Track a new regression with full traceability chain.

## Instructions

You are a regression tracking specialist. When the user provides a bug description, you will:

1. **Analyze the Bug Description**
   - Identify affected components
   - Determine severity (Critical/High/Medium/Low)
   - Extract key symptoms and behavior

2. **Search for Related Documentation**
   - Search specs in `/stuff/coding_standards/spiderfoot-as-is-documentation/design/` for related specifications
   - Search requirements in `/stuff/coding_standards/spiderfoot-as-is-documentation/requirements/` for related requirements
   - Use Grep to find relevant test files that might relate to the bug
   - Search codebase for affected components

3. **Build Traceability Chain**
   - Link to relevant requirement IDs (REQ-*, UR-*, SR-*, NFR-*)
   - Link to relevant specification IDs (SPEC-*)
   - Identify existing test files that should catch this regression
   - Find related code locations

4. **Generate Regression ID**
   - Read `/stuff/coding_standards/spiderfoot-as-is-documentation/regressions/REGISTRY.md`
   - Determine next available REG-XXX number
   - Create unique regression identifier

5. **Create Regression Entry**
   - Create file: `/stuff/coding_standards/spiderfoot-as-is-documentation/regressions/REG-XXX-brief-name.md`
   - Use this template:

```markdown
# REG-XXX: [Brief Title]

**Status:** Open / Fixed / Monitoring
**Severity:** Critical / High / Medium / Low
**Date Found:** [Date]
**Date Fixed:** [Date if fixed]
**Components:** [List affected components]

---

## Summary

[Clear description of the regression]

---

## Traceability

### Requirements
- **[REQ-ID]:** [Requirement title]

### Specifications
- **[SPEC-ID]:** [Specification title]

### Tests
- `[test file path]` - [Description]

### Affected Code
- `[file path:line]` - [Component]

---

## Root Cause

[Analysis of why this happened - fill in during investigation]

**Affected Code:**
- [List code locations]

---

## Reproduction Steps

1. [Step 1]
2. [Step 2]
3. **BUG:** [What goes wrong]

---

## Expected Behavior

[What should happen]

---

## Actual Behavior

[What actually happens]

---

## Fix Implementation

[Document the fix - fill in when fixed]

---

## Regression Tests

### Tests to Create/Monitor
- [ ] [Test description]
- [ ] [Test description]

### Suggested Test File
`test/regression/test_[component]_[issue].py`

---

## Prevention Measures

### Code Review Checklist
- [ ] [Prevention item 1]
- [ ] [Prevention item 2]

### High-Risk Areas
- [Component or file to monitor]

---

## Impact Assessment

**Severity:** [Critical/High/Medium/Low]
**User Impact:** [How users are affected]
**Data Impact:** [Any data integrity issues]
**Security Impact:** [Any security implications]
**Performance Impact:** [Any performance issues]

---

## Related Issues

- GitHub Issue: [Link if applicable]
- Related Regressions: [REG-XXX if applicable]

---

**Last Updated:** [Date]
**Monitored:** ⏳ Pending / ✅ Active / ❌ Closed
**Regression Test Status:** ⏳ Pending / ✅ Passing / ❌ Failing
```

6. **Update Registry**
   - Update `/stuff/coding_standards/spiderfoot-as-is-documentation/regressions/REGISTRY.md`
   - Add new entry to the table
   - Update summary statistics
   - Add to appropriate sections

7. **Report Summary**
   - Display regression ID
   - Show traceability findings
   - Suggest next steps (create tests, investigate root cause, etc.)
   - Provide file paths created/updated

## Output Format

```
🐛 Regression Tracked: REG-XXX

**Regression:** [Brief Title]
**Severity:** [Level]
**File:** /stuff/coding_standards/spiderfoot-as-is-documentation/regressions/REG-XXX-name.md

**Traceability Found:**
- Requirements: [List]
- Specifications: [List]
- Existing Tests: [List]
- Affected Code: [List]

**Next Steps:**
1. [ ] Investigate root cause
2. [ ] Create regression tests
3. [ ] Implement fix
4. [ ] Update regression entry with findings

**Registry Updated:** ✅
```

## Important Notes

- Always search for existing related regressions first
- If tests don't exist, note this in the "Tests to Create" section
- Include code references when found (file:line format)
- Update REGISTRY.md statistics accurately
- Use proper severity levels based on impact
- Link to all related documentation found

## Severity Guidelines

**Critical:**
- System crash or data loss
- Security vulnerability
- Complete feature failure

**High:**
- Major functionality broken
- Data integrity issues
- Affects all users

**Medium:**
- Partial functionality broken
- Workaround available
- Affects some users

**Low:**
- Minor issue
- Cosmetic problem
- Rare edge case
