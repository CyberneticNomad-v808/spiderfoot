#!/usr/bin/env python3
"""
Setup Agent Coordination System
Initializes Redis with task queue and configuration
"""

import redis
from agent_coordination import TaskQueue, AgentCoordinator

def setup_coordination(redis_host: str = "redis.blk.ing"):
    """Initialize Redis coordination system"""
    
    print("🚀 Setting up Agent Coordination System")
    print(f"   Redis: {redis_host}")
    print()
    
    # Connect to Redis
    r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    
    try:
        r.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return False
    
    # Clear old coordination data (optional)
    print("\n🧹 Cleaning up old coordination data...")
    for key in r.scan_iter("agent:*"):
        r.delete(key)
    for key in r.scan_iter("tasks:*"):
        r.delete(key)
    for key in r.scan_iter("lock:*"):
        r.delete(key)
    for key in r.scan_iter("decision:*"):
        r.delete(key)
    r.delete("activity:stream")
    r.delete("agents:all")
    print("✅ Cleanup complete")
    
    # Populate task queue
    print("\n📋 Populating task queue...")
    queue = TaskQueue(redis_host=redis_host)
    queue.populate_test_fix_tasks()
    
    # Set initial decisions/configuration
    print("\n⚙️  Setting initial configuration...")
    config_agent = AgentCoordinator("setup", redis_host=redis_host)
    
    config_agent.share_decision(
        "redis_host",
        "redis.blk.ing",
        "Central Redis instance for agent coordination"
    )
    
    config_agent.share_decision(
        "postgresql_host",
        "unified-postgres.blk.ing:5432",
        "PostgreSQL database for test persistence"
    )
    
    config_agent.log("Coordination system initialized", level="INFO")
    
    print("✅ Configuration complete")
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 COORDINATION SYSTEM READY")
    print("=" * 60)
    
    queue_stats = {
        "pending": r.llen("tasks:queue"),
        "priority_1": r.llen("tasks:priority:1"),
        "priority_2": r.llen("tasks:priority:2"),
        "priority_3": r.llen("tasks:priority:3"),
    }
    
    print(f"   Tasks in queue:     {queue_stats['pending']}")
    print(f"   Priority 1 (Crit):  {queue_stats['priority_1']}")
    print(f"   Priority 2 (High):  {queue_stats['priority_2']}")
    print(f"   Priority 3 (Med):   {queue_stats['priority_3']}")
    print()
    print("🚀 Next steps:")
    print("   1. Start monitoring: python3 monitor_agents.py")
    print("   2. Deploy agents with: python3 your_agent_script.py")
    print()
    
    return True


if __name__ == "__main__":
    import sys
    
    redis_host = sys.argv[1] if len(sys.argv) > 1 else "redis.blk.ing"
    
    success = setup_coordination(redis_host)
    sys.exit(0 if success else 1)
