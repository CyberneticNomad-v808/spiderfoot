  Step 1: Create a Local Branch from Upstream dev-5.3.3

  # Create a new local branch tracking upstream's dev-5.3.3
  git checkout -b local-dev-5.3.3 upstream/dev-5.3.3

  # Switch back to master
  git checkout master

  Now you have:
  - master - your working branch with your fixes
  - local-dev-5.3.3 - their refactored code (local only, not pushed)

  Step 2: Create Feature Branches for Each Improvement

  For each feature you want to adopt, create a topic branch:

  # Example: Cherry-pick just the new TikTok module
  git checkout -b feature/add-tiktok-module master
  git checkout local-dev-5.3.3 -- modules/sfp_tiktok_osint.py
  git add modules/sfp_tiktok_osint.py
  git commit -m "Add TikTok OSINT module from upstream dev-5.3.3"

  Step 3: Methodical Integration Strategy

  I recommend this order to preserve your fixes:

  Phase 1: Low-Risk New Modules (no conflicts with your code)

  # 1. Add new standalone modules one at a time
  git checkout -b feature/blockchain-analytics master
  git checkout local-dev-5.3.3 -- modules/sfp_blockchain_analytics.py
  git commit -m "Add blockchain analytics module"

  git checkout -b feature/advanced-correlation master
  git checkout local-dev-5.3.3 -- modules/sfp_advanced_correlation.py
  git commit -m "Add advanced correlation module"

  git checkout -b feature/performance-optimizer master
  git checkout local-dev-5.3.3 -- modules/sfp_performance_optimizer.py
  git commit -m "Add performance optimizer module"

  Phase 2: Infrastructure Improvements (test thoroughly)

  # 2. Add thread leak fixes (carefully review for compatibility)
  git checkout -b feature/thread-leak-fixes master
  # Manually identify and cherry-pick specific commits
  git cherry-pick <commit-hash-of-thread-fix>

  Phase 3: Documentation & Deployment Tools

  # 3. Add production deployment configs
  git checkout -b feature/production-deployment master
  git checkout local-dev-5.3.3 -- docker-compose-examples/
  git commit -m "Add production deployment configurations"

  Phase 4: Refactoring (LAST - most risky)

  # Only if you want the modular architecture
  # This would be a major undertaking requiring careful migration of YOUR fixes
  git checkout -b feature/modular-refactor master
  # This needs manual work to merge their structure with your fixes

  Step 4: Create Pull Requests to Master

  For each feature branch:

  # Push feature branch to YOUR origin
  git checkout feature/add-tiktok-module
  git push origin feature/add-tiktok-module

  # Create PR via GitHub CLI or web interface
  gh pr create --base master --head feature/add-tiktok-module \
    --title "Add TikTok OSINT module" \
    --body "Cherry-picked from upstream dev-5.3.3. Adds TikTok user/content analysis capabilities."

  Step 5: Testing Protocol for Each PR

  Before merging each PR:

  # On the feature branch
  pytest test/
  python sf.py --modules  # Verify module loads
  python sf.py -s test.com -m sfp_tiktok_osint  # Test the specific module

  Recommended Order of PRs:

  1. PR #1: Add blockchain analytics module (safest, standalone)
  2. PR #2: Add TikTok OSINT module
  3. PR #3: Add advanced correlation module
  4. PR #4: Add performance optimizer module
  5. PR #5: Production deployment configs
  6. PR #6: Documentation improvements
  7. PR #7: Thread leak fixes (review carefully for conflicts with your proxy fixes)
  8. PR #8+: Any other specific improvements you identify

  Preserving Your Fixes

  Your PostgreSQL and proxy fixes in these files will be preserved because you're cherry-picking FROM local-dev-5.3.3 INTO master, not the other way around:

  - spiderfoot/db.py - Your PostgreSQL placeholders stay
  - modules/sfp_* - Your proxy fixes stay
  - sf.py - Your PostgreSQL configuration logic stays

  Commands Summary:

  # Setup
  git checkout -b local-dev-5.3.3 upstream/dev-5.3.3
  git checkout master

  # For each feature (repeat pattern)
  git checkout -b feature/FEATURE_NAME master
  git checkout local-dev-5.3.3 -- path/to/files
  git add path/to/files
  git commit -m "Descriptive message"
  git push origin feature/FEATURE_NAME
  gh pr create --base master --head feature/FEATURE_NAME --title "Title" --body "Description"

  # After PR review and approval
  git checkout master
  git merge feature/FEATURE_NAME
  git push origin master