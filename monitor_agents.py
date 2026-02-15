#!/usr/bin/env python3
"""
Real-time Agent Monitoring Dashboard
Displays agent activity, progress, and coordination via Redis
"""

import redis
import json
import time
import sys
from datetime import datetime
from typing import Dict, List
import threading

class AgentMonitor:
    """Real-time monitoring of agent coordination via Redis"""
    
    def __init__(self, redis_host: str = "redis.blk.ing", redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_timeout=5
        )
        self.running = True
        
    def clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        agents_data = self.redis_client.hgetall("agents:all")
        agents = {}
        for agent_id, data in agents_data.items():
            try:
                agents[agent_id] = json.loads(data)
            except:
                agents[agent_id] = {"error": "Invalid data"}
        return agents
    
    def get_file_locks(self) -> Dict[str, str]:
        """Get all current file locks"""
        locks = {}
        for key in self.redis_client.scan_iter("lock:file:*"):
            file_path = key.replace("lock:file:", "")
            holder = self.redis_client.get(key)
            locks[file_path] = holder
        return locks
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent activity from all agents"""
        activity_items = self.redis_client.lrange("activity:stream", 0, limit - 1)
        activities = []
        for item in activity_items:
            try:
                activities.append(json.loads(item))
            except:
                pass
        return activities
    
    def get_decisions(self) -> Dict[str, Dict]:
        """Get all shared decisions"""
        decisions = {}
        for key in self.redis_client.scan_iter("decision:*"):
            decision_key = key.replace("decision:", "")
            data = self.redis_client.get(key)
            try:
                decisions[decision_key] = json.loads(data)
            except:
                pass
        return decisions
    
    def get_task_queue_status(self) -> Dict:
        """Get task queue statistics"""
        return {
            "pending": self.redis_client.llen("tasks:queue"),
            "completed": self.redis_client.llen("tasks:completed"),
            "priority_1": self.redis_client.llen("tasks:priority:1"),
            "priority_2": self.redis_client.llen("tasks:priority:2"),
            "priority_3": self.redis_client.llen("tasks:priority:3"),
        }
    
    def format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp for display"""
        try:
            dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
            return dt.strftime("%H:%M:%S")
        except:
            return iso_timestamp[:8]
    
    def render_dashboard(self):
        """Render the monitoring dashboard"""
        self.clear_screen()
        
        print("=" * 100)
        print("🤖 AGENT COORDINATION MONITOR - SpiderFoot Test Fixes")
        print(f"📡 Connected to: redis.blk.ing | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        print()
        
        # Agent Status
        print("👥 ACTIVE AGENTS")
        print("-" * 100)
        agents = self.get_agent_status()
        if agents:
            for agent_id, status in agents.items():
                status_emoji = {
                    "READY": "🟢",
                    "WORKING": "🔵",
                    "WAITING": "🟡",
                    "ERROR": "🔴",
                    "SHUTDOWN": "⚫"
                }.get(status.get("status", ""), "⚪")
                
                task = status.get("current_task", "Idle")
                last_update = self.format_timestamp(status.get("last_update", ""))
                
                print(f"{status_emoji} {agent_id:25} | {status.get('status', 'UNKNOWN'):10} | {task[:40]:40} | {last_update}")
        else:
            print("   No agents currently active")
        print()
        
        # File Locks
        print("🔒 FILE LOCKS")
        print("-" * 100)
        locks = self.get_file_locks()
        if locks:
            for file_path, holder in list(locks.items())[:5]:
                print(f"   📄 {file_path:60} | Locked by: {holder}")
            if len(locks) > 5:
                print(f"   ... and {len(locks) - 5} more files")
        else:
            print("   No files currently locked")
        print()
        
        # Task Queue Status
        print("📋 TASK QUEUE STATUS")
        print("-" * 100)
        queue_status = self.get_task_queue_status()
        print(f"   ⏳ Pending:    {queue_status['pending']:3} tasks")
        print(f"   ✅ Completed:  {queue_status['completed']:3} tasks")
        print(f"   🔴 Priority 1: {queue_status['priority_1']:3} (Critical)")
        print(f"   🟡 Priority 2: {queue_status['priority_2']:3} (High)")
        print(f"   🟢 Priority 3: {queue_status['priority_3']:3} (Medium)")
        print()
        
        # Shared Decisions
        print("🎯 SHARED DECISIONS")
        print("-" * 100)
        decisions = self.get_decisions()
        if decisions:
            for key, decision in list(decisions.items())[:3]:
                made_by = decision.get("made_by", "unknown")
                value = decision.get("decision", "")
                print(f"   📌 {key:40} = {value[:35]:35} (by {made_by})")
        else:
            print("   No decisions recorded yet")
        print()
        
        # Recent Activity
        print("📊 RECENT ACTIVITY (last 10 events)")
        print("-" * 100)
        activities = self.get_recent_activity(10)
        for activity in activities:
            timestamp = self.format_timestamp(activity.get("timestamp", ""))
            agent = activity.get("agent_id", "unknown")[:20]
            level = activity.get("level", "INFO")
            message = activity.get("message", "")[:50]
            
            level_emoji = {
                "INFO": "ℹ️",
                "WARN": "⚠️",
                "ERROR": "❌",
                "SUCCESS": "✅"
            }.get(level, "•")
            
            print(f"   {timestamp} | {level_emoji} {agent:20} | {message}")
        
        print()
        print("=" * 100)
        print("Press Ctrl+C to exit monitoring")
        print("=" * 100)
    
    def monitor_live_stream(self):
        """Monitor live activity stream via pub/sub"""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("agent:activity", "decisions")
        
        print("\n🔴 LIVE STREAM (new events will appear below)")
        print("-" * 100)
        
        for message in pubsub.listen():
            if not self.running:
                break
                
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    timestamp = self.format_timestamp(data.get("timestamp", ""))
                    agent = data.get("agent_id", "system")[:20]
                    msg = data.get("message", data.get("decision", ""))[:60]
                    print(f"⚡ {timestamp} | {agent:20} | {msg}")
                    sys.stdout.flush()
                except:
                    pass
    
    def run_dashboard(self, refresh_interval: int = 2):
        """Run the dashboard with periodic refresh"""
        
        # Start live stream monitor in background thread
        stream_thread = threading.Thread(target=self.monitor_live_stream, daemon=True)
        stream_thread.start()
        
        try:
            while self.running:
                self.render_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            self.running = False
            print("\n\n👋 Monitoring stopped")
    
    def export_logs(self, output_file: str = "agent_logs.json"):
        """Export all agent logs to JSON file"""
        all_logs = {
            "agents": self.get_agent_status(),
            "activity": self.get_recent_activity(1000),
            "decisions": self.get_decisions(),
            "locks": self.get_file_locks(),
            "queue_status": self.get_task_queue_status(),
            "exported_at": datetime.utcnow().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(all_logs, f, indent=2)
        
        print(f"✅ Logs exported to {output_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor AI agents coordinating via Redis")
    parser.add_argument("--host", default="redis.blk.ing", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument("--export", help="Export logs to JSON file and exit")
    parser.add_argument("--refresh", type=int, default=2, help="Dashboard refresh interval (seconds)")
    
    args = parser.parse_args()
    
    monitor = AgentMonitor(redis_host=args.host, redis_port=args.port)
    
    if args.export:
        monitor.export_logs(args.export)
    else:
        print("🚀 Starting agent monitoring dashboard...")
        print("   Connecting to redis.blk.ing...")
        time.sleep(1)
        monitor.run_dashboard(refresh_interval=args.refresh)


if __name__ == "__main__":
    main()
