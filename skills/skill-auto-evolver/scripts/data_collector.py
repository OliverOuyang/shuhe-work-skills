"""Data collector for skill execution metrics."""
import sqlite3
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import uuid

class ExecutionContext:
    def __init__(self, skill_name: str, input_params: dict, output_result: dict,
                 success: bool, duration_ms: int, error_trace: Optional[str] = None):
        self.skill_name = skill_name
        self.input_params = input_params
        self.output_result = output_result
        self.success = success
        self.duration_ms = duration_ms
        self.error_trace = error_trace

class DataCollector:
    def __init__(self, db_path: str = ".omc/evolution/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                execution_id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                input_params TEXT,
                output_result TEXT,
                success BOOLEAN NOT NULL,
                duration_ms INTEGER NOT NULL,
                error_trace TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_timestamp 
            ON executions(skill_name, timestamp)
        """)
        
        conn.commit()
        conn.close()

    def capture_execution(self, context: ExecutionContext) -> str:
        """Capture an execution and return execution_id."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        execution_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        cursor.execute("""
            INSERT INTO executions 
            (execution_id, skill_name, timestamp, input_params, output_result,
             success, duration_ms, error_trace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_id,
            context.skill_name,
            timestamp,
            json.dumps(context.input_params),
            json.dumps(context.output_result),
            context.success,
            context.duration_ms,
            context.error_trace
        ))
        
        conn.commit()
        conn.close()
        
        return execution_id

    def get_execution_history(self, skill_name: str, limit: int = 100) -> List[Dict]:
        """Get recent execution history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT execution_id, timestamp, success, duration_ms, error_trace
            FROM executions
            WHERE skill_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (skill_name, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "execution_id": row[0],
                "timestamp": datetime.fromtimestamp(row[1]).isoformat(),
                "success": bool(row[2]),
                "duration_ms": row[3],
                "error_trace": row[4]
            })
        
        conn.close()
        return results

    def calculate_metrics(self, skill_name: str, window_days: int = 30) -> Dict:
        """Calculate performance metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = int((datetime.now().timestamp() - (window_days * 86400)))
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(duration_ms) as avg_duration,
                MIN(duration_ms) as min_duration,
                MAX(duration_ms) as max_duration
            FROM executions
            WHERE skill_name = ? AND timestamp >= ?
        """, (skill_name, cutoff))
        
        row = cursor.fetchone()
        
        if row and row[0] > 0:
            total, successes, avg_dur, min_dur, max_dur = row
            success_rate = (successes / total) * 100
            
            # Calculate percentiles
            cursor.execute("""
                SELECT duration_ms FROM executions
                WHERE skill_name = ? AND timestamp >= ? AND success = 1
                ORDER BY duration_ms
            """, (skill_name, cutoff))
            
            durations = [r[0] for r in cursor.fetchall()]
            p50 = durations[len(durations)//2] if durations else 0
            p95 = durations[int(len(durations)*0.95)] if durations else 0
            p99 = durations[int(len(durations)*0.99)] if durations else 0
            
            conn.close()
            
            return {
                "skill_name": skill_name,
                "window_days": window_days,
                "total_executions": total,
                "success_rate": round(success_rate, 2),
                "avg_duration_ms": round(avg_dur, 2) if avg_dur else 0,
                "min_duration_ms": min_dur,
                "max_duration_ms": max_dur,
                "p50_latency_ms": p50,
                "p95_latency_ms": p95,
                "p99_latency_ms": p99
            }
        
        conn.close()
        return {}

if __name__ == "__main__":
    collector = DataCollector()
    ctx = ExecutionContext("test-skill", {"arg": "value"}, {"result": "ok"}, 
                          True, 1500)
    exec_id = collector.capture_execution(ctx)
    print(f"Captured: {exec_id}")
