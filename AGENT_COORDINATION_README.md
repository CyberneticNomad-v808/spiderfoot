# Agent Coordination System

Redis-based coordination for multiple AI agents fixing SpiderFoot test failures.

## Quick Start

### 1. Initialize the Coordination System
```bash
python3 setup_agent_coordination.py
```

This will:
- Connect to `redis.blk.ing`
- Clear old coordination data
- Populate task queue with 14 tasks from root cause analysis
- Set up initial configuration

### 2. Start Monitoring Dashboard
```bash
python3 monitor_agents.py
```

This displays real-time:
- 👥 Active agents and their status
- 🔒 File locks
- 📋 Task queue statistics
- 🎯 Shared decisions
- 📊 Recent activity stream

**Press Ctrl+C to exit**

### 3. Run Your Agents

Each agent should use the `AgentCoordinator` class:

```python
from agent_coordination import AgentCoordinator

# Initialize
agent = AgentCoordinator("agent-db-team")
agent.log("Agent started")
agent.update_status("READY")

# Claim and work on tasks
while True:
    task = agent.claim_task()
    if not task:
        break
    
    agent.update_status("WORKING", current_task=task['description'])
    
    # Lock files before editing
    try:
        with agent.file_lock(task['files'][0]):
            agent.log(f"Working on {task['files'][0]}")
            
            # DO YOUR WORK HERE
            # ...
            
            agent.complete_task(task, {"status": "success"})
            agent.report_progress("tests_fixed", 5)
    except RuntimeError as e:
        agent.log(f"File lock conflict: {e}", level="WARN")

agent.shutdown()
```

## Features

### File Locking
```python
with agent.file_lock("spiderfoot/db/db_core.py"):
    # Only this agent can edit this file
    # Lock expires after 5 minutes
```

### Progress Reporting
```python
agent.report_progress("tests_fixed", 12)
agent.report_progress("lines_removed", 450)
```

### Shared Decisions
```python
# Make a decision
agent.share_decision(
    "opts_architecture",
    "Option C: Separate global_opts from module_opts",
    "Cleaner separation of concerns"
)

# Read a decision made by another agent
decision = agent.get_decision("opts_architecture")
```

### Conflict Detection
```python
conflicts = agent.check_conflicts([
    "test/conftest.py",
    "spiderfoot/db/db_core.py"
])
if conflicts:
    print(f"Files locked: {conflicts}")
```

## Task Queue Structure

Tasks are prioritized:
- **Priority 1** (Critical): SQLite removal - 5 tasks
- **Priority 2** (High): Config/opts fixes - 4 tasks
- **Priority 3** (Medium): URL validation, API retry - 5 tasks

Each task includes:
```json
{
  "id": "task_1708012345678",
  "description": "Remove SQLite code from db_core.py",
  "root_cause": 1,
  "priority": 1,
  "files": ["spiderfoot/db/db_core.py"],
  "details": {"removes": ["SQLite detection", "SQLite connection code"]}
}
```

## Monitoring Options

### Export Logs
```bash
python3 monitor_agents.py --export agent_logs.json
```

### Custom Refresh Rate
```bash
python3 monitor_agents.py --refresh 5  # Update every 5 seconds
```

### Different Redis Host
```bash
python3 monitor_agents.py --host localhost --port 6379
```

## Redis Data Structure

### Keys
- `agents:all` - Hash of all agent statuses
- `agent:{id}:log` - Agent activity log
- `agent:{id}:status` - Agent current status
- `agent:{id}:metrics` - Agent performance metrics
- `activity:stream` - Global activity stream
- `tasks:queue` - Main task queue
- `tasks:priority:{1,2,3}` - Priority-based queues
- `tasks:completed` - Completed tasks
- `lock:file:{path}` - File locks
- `decision:{key}` - Shared decisions

### Pub/Sub Channels
- `agent:activity` - Live activity stream
- `decisions` - Decision announcements

## Example Agent Output

```
🟢 agent-db-team       | WORKING    | Remove SQLite code from db_core.py   | 19:05:23
🔵 agent-config-team   | WAITING    | Waiting for decision:opts_architecture| 19:05:20
🟢 agent-quality-team  | WORKING    | Add null check to network.py:187     | 19:05:18
```

## Troubleshooting

### Can't connect to Redis
```bash
ping redis.blk.ing
telnet redis.blk.ing 6379
```

### Clear all coordination data
```bash
redis-cli -h redis.blk.ing FLUSHDB
python3 setup_agent_coordination.py
```

### View raw Redis data
```bash
redis-cli -h redis.blk.ing
> KEYS agent:*
> HGETALL agents:all
> LRANGE activity:stream 0 10
```

## Next Steps

See `TEST_FAILURE_ROOT_CAUSE_ANALYSIS.md` for detailed fix instructions for each root cause.
