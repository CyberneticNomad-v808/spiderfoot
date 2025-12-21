#!/bin/bash
#
# SpiderFoot Test Reminder Script
# Checks if tests haven't been run recently and reminds user
#
# Usage: Run via cron or manually
#   0 9 * * * /stuff/spiderfoot/.claude/scripts/test-reminder.sh
#

cd /stuff/spiderfoot || exit 1

# Check if Redis is available
if ! docker exec unified-redis redis-cli -h redis -p 6379 PING &>/dev/null; then
    echo "⚠️  Redis unavailable - cannot check last test run"
    exit 0
fi

# Get last test run timestamp from Redis
last_run=$(docker exec unified-redis redis-cli -h redis -p 6379 GET test:last_run 2>/dev/null || echo "0")

if [ -z "$last_run" ] || [ "$last_run" = "(nil)" ]; then
    last_run=0
fi

# Calculate days since last run
current_time=$(date +%s)
days_ago=$(( (current_time - last_run) / 86400 ))

# Remind if tests haven't run in 1+ days
if [ $days_ago -ge 1 ]; then
    echo "⚠️  SpiderFoot tests haven't run in $days_ago day(s)!"
    echo ""
    echo "Quick test: /test unit --quick"
    echo "Full test:  /test all --parallel --cov"
    echo ""
    echo "Last run: $(date -d @"$last_run" 2>/dev/null || echo 'Never')"
else
    echo "✅ Tests are current (last run: $(date -d @"$last_run" '+%Y-%m-%d %H:%M'))"
fi
