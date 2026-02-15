#!/usr/bin/env python3
"""
Agent Coordination System via Redis
Allows multiple AI agents to coordinate test fixes with real-time monitoring
"""

import redis
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

class AgentCoordinator:
    """Coordinates multiple agents working on test fixes via Redis"""
    
    def __init__(self, agent_id: str, redis_host: str = "redis.blk.ing", redis_port: int = 6379):
        self.agent_id = agent_id
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        self.lock_timeout = 300  # 5 minutes
        
    def log(self, message: str, level: str = "INFO", data: Optional[Dict] = None):
        """Log agent activity to Redis"""
        log_entry = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        }
        
        # Add to agent-specific log
        self.redis_client.lpush(
            f"agent:{self.agent_id}:log",
            json.dumps(log_entry)
        )
        # Trim to last 1000 entries
        self.redis_client.ltrim(f"agent:{self.agent_id}:log", 0, 999)
        
        # Add to global activity stream
        self.redis_client.lpush("activity:stream", json.dumps(log_entry))
        self.redis_client.ltrim("activity:stream", 0, 4999)
        
        # Publish to live monitoring channel
        self.redis_client.publish("agent:activity", json.dumps(log_entry))
        
    def update_status(self, status: str, current_task: Optional[str] = None, progress: Optional[Dict] = None):
        """Update agent status"""
        status_data = {
            "agent_id": self.agent_id,
            "status": status,
            "current_task": current_task,
            "progress": progress or {},
            "last_update": datetime.utcnow().isoformat()
        }
        
        # Store in hash for easy querying
        self.redis_client.hset(
            f"agent:{self.agent_id}:status",
            mapping=status_data
        )
        
        # Also store in global agent list
        self.redis_client.hset("agents:all", self.agent_id, json.dumps(status_data))
        
        self.log(f"Status updated: {status}", data=status_data)
        
    @contextmanager
    def file_lock(self, file_path: str):
        """Context manager for file locking"""
        lock_key = f"lock:file:{file_path}"
        lock_acquired = False
        
        try:
            # Try to acquire lock
            lock_acquired = self.redis_client.set(
                lock_key,
                self.agent_id,
                ex=self.lock_timeout,
                nx=True
            )
            
            if not lock_acquired:
                # Check who has the lock
                current_holder = self.redis_client.get(lock_key)
                self.log(
                    f"Failed to acquire lock on {file_path}",
                    level="WARN",
                    data={"current_holder": current_holder}
                )
                raise RuntimeError(f"File {file_path} is locked by {current_holder}")
            
            self.log(f"Acquired lock on {file_path}")
            yield
            
        finally:
            if lock_acquired:
                # Release lock only if we hold it
                current = self.redis_client.get(lock_key)
                if current == self.agent_id:
                    self.redis_client.delete(lock_key)
                    self.log(f"Released lock on {file_path}")
    
    def claim_task(self, queue_name: str = "tasks:queue") -> Optional[Dict]:
        """Claim a task from the queue"""
        task_json = self.redis_client.rpop(queue_name)
        if not task_json:
            return None
            
        task = json.loads(task_json)
        task["claimed_by"] = self.agent_id
        task["claimed_at"] = datetime.utcnow().isoformat()
        
        # Store claimed task
        self.redis_client.hset(
            f"agent:{self.agent_id}:current_task",
            mapping=task
        )
        
        self.log(f"Claimed task: {task.get('description')}", data=task)
        return task
    
    def complete_task(self, task: Dict, result: Dict):
        """Mark task as completed"""
        completion = {
            "task": task,
            "result": result,
            "completed_by": self.agent_id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        # Store completion
        self.redis_client.lpush(
            "tasks:completed",
            json.dumps(completion)
        )
        
        # Update metrics
        self.redis_client.hincrby(f"agent:{self.agent_id}:metrics", "tasks_completed", 1)
        
        # Clear current task
        self.redis_client.delete(f"agent:{self.agent_id}:current_task")
        
        self.log(f"Completed task: {task.get('description')}", data=result)
    
    def report_progress(self, metric: str, value: Any):
        """Report progress metric"""
        self.redis_client.hset(
            f"agent:{self.agent_id}:metrics",
            metric,
            str(value)
        )
        
        self.log(f"Progress: {metric} = {value}", data={"metric": metric, "value": value})
    
    def share_decision(self, decision_key: str, decision: str, rationale: str):
        """Share an architectural or implementation decision"""
        decision_data = {
            "decision": decision,
            "rationale": rationale,
            "made_by": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.redis_client.set(
            f"decision:{decision_key}",
            json.dumps(decision_data)
        )
        
        self.log(f"Decision made: {decision_key} = {decision}", data=decision_data)
        
        # Publish to decision channel
        self.redis_client.publish("decisions", json.dumps(decision_data))
    
    def get_decision(self, decision_key: str) -> Optional[Dict]:
        """Get a shared decision"""
        data = self.redis_client.get(f"decision:{decision_key}")
        return json.loads(data) if data else None
    
    def check_conflicts(self, files: List[str]) -> Dict[str, str]:
        """Check which files are locked by other agents"""
        conflicts = {}
        for file_path in files:
            lock_key = f"lock:file:{file_path}"
            holder = self.redis_client.get(lock_key)
            if holder and holder != self.agent_id:
                conflicts[file_path] = holder
        return conflicts
    
    def get_all_agents(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        agents_data = self.redis_client.hgetall("agents:all")
        return {
            agent_id: json.loads(data)
            for agent_id, data in agents_data.items()
        }
    
    def shutdown(self):
        """Clean shutdown"""
        self.update_status("SHUTDOWN")
        self.log("Agent shutting down")


class TaskQueue:
    """Manages task queue for agents"""
    
    def __init__(self, redis_host: str = "redis.blk.ing", redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
    
    def add_task(self, description: str, root_cause: int, priority: int, 
                 files: List[str], details: Optional[Dict] = None):
        """Add a task to the queue"""
        task = {
            "id": f"task_{int(time.time()*1000)}",
            "description": description,
            "root_cause": root_cause,
            "priority": priority,
            "files": files,
            "details": details or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to priority queue (lower priority number = higher priority)
        queue_name = f"tasks:priority:{priority}"
        self.redis_client.lpush(queue_name, json.dumps(task))
        
        # Also add to main queue for simple pop
        self.redis_client.lpush("tasks:queue", json.dumps(task))
        
        return task["id"]
    
    def populate_test_fix_tasks(self):
        """Populate task queue with test fix tasks from root cause analysis"""
        
        # Root Cause #1: SQLite Removal (CRITICAL)
        self.add_task(
            "Remove SQLite code from db_core.py",
            root_cause=1,
            priority=1,
            files=["spiderfoot/db/db_core.py"],
            details={"removes": ["SQLite detection", "SQLite connection code"]}
        )
        
        self.add_task(
            "Remove SQLite code from db/__init__.py",
            root_cause=1,
            priority=1,
            files=["spiderfoot/db/__init__.py"]
        )
        
        self.add_task(
            "Add Redis support to sfp__stor_db.py for temporary storage",
            root_cause=1,
            priority=1,
            files=["modules/sfp__stor_db.py"],
            details={"adds": ["Redis client", "Temporary storage methods"]}
        )
        
        self.add_task(
            "Update test/conftest.py for PostgreSQL-only tests",
            root_cause=1,
            priority=1,
            files=["test/conftest.py"],
            details={"removes": ["SQLite test config"], "adds": ["PostgreSQL fixtures"]}
        )
        
        self.add_task(
            "Create PostgreSQL test fixtures with transaction rollback",
            root_cause=1,
            priority=1,
            files=["test/fixtures/database_fixtures.py"],
            details={"adds": ["Transaction-based test isolation"]}
        )
        
        # Root Cause #2: Module Options Mismatch
        self.add_task(
            "Investigate module configuration merge in SpiderFootPlugin",
            root_cause=2,
            priority=2,
            files=["spiderfoot/sflib/plugin.py"],
            details={"investigates": ["opts/optdescs merge behavior"]}
        )
        
        self.add_task(
            "Fix opts/optdescs mismatch (implementation depends on architectural decision)",
            root_cause=2,
            priority=2,
            files=["modules/*.py"],  # Will be updated after investigation
            details={"depends_on": "decision:opts_architecture"}
        )
        
        # Root Cause #3: Storage Module Configuration
        self.add_task(
            "Fix test environment variable isolation",
            root_cause=3,
            priority=2,
            files=["test/conftest.py"],
            details={"moves": ["env vars to fixtures"], "adds": ["monkeypatch usage"]}
        )
        
        self.add_task(
            "Fix module environment variable reading",
            root_cause=3,
            priority=2,
            files=["modules/sfp__stor_db.py"]
        )
        
        # Root Cause #4: URL Validation
        self.add_task(
            "Add null check to spiderfoot/sflib/network.py:187",
            root_cause=4,
            priority=3,
            files=["spiderfoot/sflib/network.py"],
            details={"line": 187, "adds": ["None check before .lower()"]}
        )
        
        self.add_task(
            "Audit all urlFQDN() callers for similar bugs",
            root_cause=4,
            priority=3,
            files=["spiderfoot/sflib/*.py"]
        )
        
        # Root Cause #5: External API Tests
        self.add_task(
            "Add retry configuration to .env.template",
            root_cause=5,
            priority=3,
            files=[".env.template"],
            details={"adds": ["API_TEST_MAX_RETRIES", "API_TEST_RETRY_DELAY", "API_TEST_TIMEOUT"]}
        )
        
        self.add_task(
            "Implement retry decorator for external API tests",
            root_cause=5,
            priority=3,
            files=["test/utils/external_api.py"],
            details={"creates": ["Retry decorator", "Pytest markers"]}
        )
        
        self.add_task(
            "Apply retry logic to Cisco Umbrella tests",
            root_cause=5,
            priority=3,
            files=["test/integration/modules/test_sfp_cisco_umbrella.py"]
        )
        
        print("✅ Task queue populated with test fix tasks")


if __name__ == "__main__":
    # Example usage
    coordinator = AgentCoordinator("example-agent")
    coordinator.log("Agent started")
    coordinator.update_status("READY")
    
    # Example: Try to work on a file
    try:
        with coordinator.file_lock("spiderfoot/db/db_core.py"):
            coordinator.log("Working on db_core.py")
            time.sleep(2)
    except RuntimeError as e:
        print(f"Lock conflict: {e}")
    
    coordinator.shutdown()
