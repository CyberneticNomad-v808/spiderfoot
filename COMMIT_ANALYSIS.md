# Master Branch Commit Analysis
## Merge Range: 6b1b331e..94054998 (682 commits)

### 🔴 CRITICAL - DO NOT CHERRY-PICK

**Commit ae60ae37** - "rc1" (2025-03-15)
- **DELETES react-web-interface/** (27 files, ~1970 lines)
- Deletes modules/sfp_xref.py (188 lines)
- Modifies storage modules (sfp__stor_db.py, sfp__stor_elasticsearch.py, sfp__stor_stdout.py)
- **Recommendation:** SKIP THIS COMMIT

### 📊 Commit Breakdown

**Total Commits:** 682

**Categories:**
- **Dependency Updates (Dependabot):** ~158 commits
- **Test Fixes:** ~71 commits
- **Bug Fixes:** ~20+ commits
- **Refactoring:** ~15+ commits
- **PostgreSQL Support:** ~15+ commits- **Features/Enhancements:** ~403 remaining

### 🟢 POTENTIALLY VALUABLE COMMITS

#### Recent Important Commits (Last 50)
[ ] **94054998** - Delete .github/FUNDING.yml (minor cleanup)
[ ] **78a8237d** - Delete .github/workflows/codacy.yml (workflow cleanup)
[ ] **d720a48c** - Delete .github/workflows/wiki-sync.yml (workflow cleanup)
[x] **71be0155** - Implement workspace multiscan with DOMAIN_NAME to INTERNET_NAME fix ⭐
[x] **9f79ffe7** - Fix proxy handling from prod-_808_-5.2.9 ⭐
[x] **0b0fc85c** - Add configurable CSRF protection from 5.2.9 ⭐
[x] **9e9a6185** - Enhance .env.example with comprehensive production configuration ⭐
[ ] **e1e74163** - thread leak and hanging general fix ⭐
[ ] **5c1bab33** - fix(tests): Correct thread cleanup in base test teardown ⭐

#### PostgreSQL Improvements
[x] - Multiple commits fixing PostgreSQL compatibility
[x] - Placeholder bugs fixed
[x] - Connection state management improved

### 🟡 DEPENDENCY UPDATES (~158 commits)

[] Most are Dependabot PRs updating:
[] - Python packages (cryptography, elasticsearch, pytest, etc.)
[x] - Test dependencies
[] - Security updates
[] - look the bi guys and bring themn down later.
**Recommendation:** These are safe to cherry-pick in batches

### 📝 ANALYSIS SUMMARY

**What You Should Do:**

1. **Skip entirely:**
   - ae60ae37 (deletes react-web-interface)
   - Any commits that delete features you want to keep

2. **Cherry-pick in order:**
   - Bug fixes (especially proxy, CSRF, thread cleanup)
   - PostgreSQL improvements (if you use PostgreSQL)
   - Security/dependency updates (do these in batches)
   - Feature enhancements (workspace multiscan, etc.)

3. **Review carefully:**
   - Refactoring commits (may conflict with your structure)
   - Test-related commits (your test suite may differ)

### 🎯 RECOMMENDED CHERRY-PICK STRATEGY

**Phase 1: Critical Bug Fixes**
```bash
git cherry-pick 9f79ffe7  # Fix proxy handling
git cherry-pick 0b0fc85c  # CSRF protection
git cherry-pick e1e74163  # Thread leak fix
git cherry-pick 5c1bab33  # Thread cleanup in tests
```

**Phase 2: Features**
```bash
git cherry-pick 71be0155  # Workspace multiscan fix
git cherry-pick 9e9a6185  # Enhanced .env.example
```

**Phase 3: Dependency Updates (batch)**
```bash
# Cherry-pick dependabot commits in groups
```

**Phase 4: PostgreSQL (if needed)**
```bash
# Cherry-pick PostgreSQL improvement commits
```

### ⚠️ NOTES

- You have 211 commits on v5.0.3-dev that master doesn't have
- Master has 682 commits you don't have
- Total divergence: 893 commits
- The branches have fundamentally different architectures

**Alternative Approach:** Consider keeping v5.0.3-dev as your main branch and only selectively pulling specific fixes/features from master that you actually need, rather than trying to merge everything.
