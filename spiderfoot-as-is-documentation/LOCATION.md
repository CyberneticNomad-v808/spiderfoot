# Documentation Location

**Current Location:** `/stuff/coding_standards/spiderfoot-as-is-documentation/`
**Previous Location:** `.claude/specs/spiderfoot-as-is/` (deprecated)
**Date Moved:** 2025-11-04

---

## Why This Location?

This documentation has been moved to `/stuff/coding_standards/` to centralize all coding standards, documentation, and best practices in one location.

---

## Structure

```
/stuff/coding_standards/spiderfoot-as-is-documentation/
├── README.md                           # Quick start guide
├── INDEX.md                            # Complete documentation index
├── SUMMARY.md                          # Project completion summary
├── LOCATION.md                         # This file
│
├── design/
│   ├── 01-system-architecture.md       # Architecture + 20 diagrams
│   └── 02-specifications-from-tests.md # 30+ specifications
│
├── requirements/
│   └── 01-functional-requirements.md   # 47+ requirements
│
├── regressions/
│   ├── REGISTRY.md                     # Regression tracking registry
│   └── REG-*.md                        # Individual regression entries
│
├── diagrams/                           # (Future: extracted diagrams)
└── tasks/                              # (Future: implementation tasks)
```

---

## Related Commands

### Slash Commands (in `.claude/commands/`)
- `/regression-track "bug description"` - Track new regressions
- `/spec-validate [feature-name]` - Validate documentation health

These commands have been updated to point to this new location.

---

## Access

**From SpiderFoot project:**
```bash
cd /stuff/coding_standards/spiderfoot-as-is-documentation/
```

**From anywhere:**
```bash
cd /stuff/coding_standards/spiderfoot-as-is-documentation/
```

---

## Maintenance

When updating documentation:
1. Update files in this location (`/stuff/coding_standards/spiderfoot-as-is-documentation/`)
2. Do NOT update the old `.claude/specs/` location
3. Use `/spec-validate` to check health after updates
4. Update regression registry when tracking new bugs

---

**Last Updated:** 2025-11-04
