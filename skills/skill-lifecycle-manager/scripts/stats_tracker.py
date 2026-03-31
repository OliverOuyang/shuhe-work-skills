"""Usage statistics tracker for skills using SQLite."""
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict

class SkillStats:
    def __init__(self, skill_name: str, total_executions: int, success_rate: float,
                 avg_duration_ms: float, last_used: str, error_count: int):
        self.skill_name = skill_name
        self.total_executions = total_executions
        self.success_rate = success_rate
        self.avg_duration_ms = avg_duration_ms
        self.last_used = last_used
        self.error_count = error_count

    def to_dict(self):
        return {
            "skill_name": self.skill_name,
            "total_executions": self.total_executions,
            "success_rate": self.success_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "last_used": self.last_used,
            "error_count": self.error_count
        }

class StatsTracker:
    def __init__(self, db_path: str = ".omc/stats/usage.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                duration_ms INTEGER NOT NULL,
                error TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_timestamp 
            ON skill_executions(skill_name, timestamp)
        """)
        
        conn.commit()
        conn.close()

    def record_skill_execution(self, skill_name: str, success: bool, 
                               duration_ms: int, error: Optional[str] = None):
        """Record a skill execution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO skill_executions (skill_name, timestamp, success, duration_ms, error)
            VALUES (?, ?, ?, ?, ?)
        """, (skill_name, timestamp, success, duration_ms, error))
        
        conn.commit()
        conn.close()

    def get_skill_stats(self, skill_name: str, days: int = 30) -> Optional[SkillStats]:
        """Get statistics for a skill over the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(duration_ms) as avg_duration,
                MAX(timestamp) as last_used,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as errors
            FROM skill_executions
            WHERE skill_name = ? AND timestamp >= ?
        """, (skill_name, cutoff))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            total, successes, avg_duration, last_used, errors = row
            success_rate = (successes / total) * 100 if total > 0 else 0
            last_used_str = datetime.fromtimestamp(last_used).isoformat() if last_used else "Never"
            
            return SkillStats(
                skill_name=skill_name,
                total_executions=total,
                success_rate=round(success_rate, 2),
                avg_duration_ms=round(avg_duration, 2) if avg_duration else 0,
                last_used=last_used_str,
                error_count=errors
            )
        
        return None

    def get_popular_skills(self, limit: int = 10, days: int = 30) -> List[SkillStats]:
        """Get most popular skills by execution count."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
        
        cursor.execute("""
            SELECT 
                skill_name,
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(duration_ms) as avg_duration,
                MAX(timestamp) as last_used,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as errors
            FROM skill_executions
            WHERE timestamp >= ?
            GROUP BY skill_name
            ORDER BY total DESC
            LIMIT ?
        """, (cutoff, limit))
        
        results = []
        for row in cursor.fetchall():
            skill_name, total, successes, avg_duration, last_used, errors = row
            success_rate = (successes / total) * 100 if total > 0 else 0
            last_used_str = datetime.fromtimestamp(last_used).isoformat() if last_used else "Never"
            
            results.append(SkillStats(
                skill_name=skill_name,
                total_executions=total,
                success_rate=round(success_rate, 2),
                avg_duration_ms=round(avg_duration, 2) if avg_duration else 0,
                last_used=last_used_str,
                error_count=errors
            ))
        
        conn.close()
        return results

    def get_problematic_skills(self, threshold: float = 0.7, days: int = 30) -> List[SkillStats]:
        """Get skills with success rate below threshold."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
        
        cursor.execute("""
            SELECT 
                skill_name,
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(duration_ms) as avg_duration,
                MAX(timestamp) as last_used,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as errors
            FROM skill_executions
            WHERE timestamp >= ?
            GROUP BY skill_name
            HAVING (CAST(successes AS FLOAT) / total) < ?
            ORDER BY (CAST(successes AS FLOAT) / total) ASC
        """, (cutoff, threshold))
        
        results = []
        for row in cursor.fetchall():
            skill_name, total, successes, avg_duration, last_used, errors = row
            success_rate = (successes / total) * 100 if total > 0 else 0
            last_used_str = datetime.fromtimestamp(last_used).isoformat() if last_used else "Never"
            
            results.append(SkillStats(
                skill_name=skill_name,
                total_executions=total,
                success_rate=round(success_rate, 2),
                avg_duration_ms=round(avg_duration, 2) if avg_duration else 0,
                last_used=last_used_str,
                error_count=errors
            ))
        
        conn.close()
        return results

if __name__ == "__main__":
    # Test the tracker
    tracker = StatsTracker()
    tracker.record_skill_execution("test-skill", True, 1500)
    tracker.record_skill_execution("test-skill", False, 2500, "Test error")
    stats = tracker.get_skill_stats("test-skill")
    if stats:
        print(f"Stats: {stats.to_dict()}")
