import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Set, Tuple
from pathlib import Path
from config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.init_db()

    def init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 1. Existing experiments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    query TEXT,
                    category TEXT,
                    complexity TEXT,
                    selected_model TEXT,
                    confidence REAL,
                    response TEXT,
                    latency REAL,
                    estimated_cost REAL,
                    quality_score REAL,
                    baseline_latency REAL,
                    baseline_cost REAL,
                    baseline_quality REAL,
                    demo_mode BOOLEAN
                )
            ''')

            # Upgrade experiments table with optional telemetry columns if not present
            cursor.execute("PRAGMA table_info(experiments)")
            existing_cols = {col[1] for col in cursor.fetchall()}
            new_cols = [
                ("execution_mode", "TEXT DEFAULT 'demo'"),
                ("model_id", "TEXT"),
                ("prompt_tokens", "INTEGER DEFAULT 0"),
                ("completion_tokens", "INTEGER DEFAULT 0"),
                ("error", "TEXT")
            ]
            for col_name, col_def in new_cols:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE experiments ADD COLUMN {col_name} {col_def}")

            # 2. Benchmark runs tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    execution_mode TEXT,
                    dataset_version TEXT,
                    total_prompts INTEGER,
                    policies TEXT,
                    status TEXT,
                    report_json TEXT
                )
            ''')

            # 3. Individual benchmark measurements table with uniqueness constraint for resumability
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    prompt_id TEXT,
                    category TEXT,
                    policy TEXT,
                    selected_model TEXT,
                    model_id TEXT,
                    latency REAL,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    cost REAL,
                    quality_score REAL,
                    eval_details TEXT,
                    response TEXT,
                    error TEXT,
                    timestamp TEXT,
                    UNIQUE(run_id, prompt_id, policy)
                )
            ''')
            conn.commit()

    def save_experiment(self, data: dict):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO experiments (
                    timestamp, query, category, complexity, selected_model, confidence, 
                    response, latency, estimated_cost, quality_score, 
                    baseline_latency, baseline_cost, baseline_quality, demo_mode,
                    execution_mode, model_id, prompt_tokens, completion_tokens, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                data.get('query'),
                data.get('category', 'unknown'),
                data.get('complexity', 'unknown'),
                data.get('selected_model'),
                data.get('confidence'),
                data.get('response'),
                data.get('latency'),
                data.get('estimated_cost'),
                data.get('quality_score'),
                data.get('baseline_latency'),
                data.get('baseline_cost'),
                data.get('baseline_quality'),
                data.get('demo_mode', True),
                data.get('execution_mode', 'demo'),
                data.get('model_id'),
                data.get('prompt_tokens', 0),
                data.get('completion_tokens', 0),
                json.dumps(data.get('error')) if isinstance(data.get('error'), (dict, list)) else (str(data.get('error')) if data.get('error') else None)
            ))
            conn.commit()

    def get_experiments(self, limit=100) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiments ORDER BY id DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_metrics(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT count(*) as count FROM experiments')
            total = cursor.fetchone()['count']
            if total == 0:
                return {}
            
            cursor.execute('''
                SELECT 
                    avg(latency) as avg_lat,
                    avg(estimated_cost) as avg_cost,
                    avg(quality_score) as avg_qual,
                    avg(baseline_latency) as avg_base_lat,
                    avg(baseline_cost) as avg_base_cost,
                    avg(baseline_quality) as avg_base_qual
                FROM experiments
            ''')
            avgs = cursor.fetchone()

            cursor.execute('SELECT count(*) as count FROM experiments WHERE error IS NOT NULL')
            failed_count = cursor.fetchone()['count']

            cursor.execute('SELECT selected_model, count(*) as count, avg(latency) as lat, avg(estimated_cost) as cost, avg(quality_score) as qual FROM experiments GROUP BY selected_model')
            models = cursor.fetchall()
            
            model_dist = {r['selected_model']: r['count'] for r in models}
            model_lat = {r['selected_model']: r['lat'] for r in models}
            model_cost = {r['selected_model']: r['cost'] for r in models}
            model_qual = {r['selected_model']: r['qual'] for r in models}

            lat_red = ((avgs['avg_base_lat'] - avgs['avg_lat']) / avgs['avg_base_lat'] * 100) if (avgs['avg_base_lat'] and avgs['avg_lat'] is not None) else None
            cost_red = ((avgs['avg_base_cost'] - avgs['avg_cost']) / avgs['avg_base_cost'] * 100) if (avgs['avg_base_cost'] and avgs['avg_cost'] is not None) else None
            qual_ret = (avgs['avg_qual'] / avgs['avg_base_qual'] * 100) if (avgs['avg_base_qual'] and avgs['avg_qual'] is not None) else None

            return {
                "total_queries": total,
                "successful_queries": total - failed_count,
                "failed_queries": failed_count,
                "failure_rate": round(failed_count / total, 4) if total else 0.0,
                "avg_latency": avgs['avg_lat'],
                "avg_cost": avgs['avg_cost'],
                "avg_quality": avgs['avg_qual'],
                "avg_baseline_latency": avgs['avg_base_lat'],
                "avg_baseline_cost": avgs['avg_base_cost'],
                "avg_baseline_quality": avgs['avg_base_qual'],
                "model_distribution": model_dist,
                "latency_by_model": model_lat,
                "cost_by_model": model_cost,
                "quality_by_model": model_qual,
                "avg_latency_reduction": (lat_red / 100) if lat_red is not None else None,
                "avg_cost_reduction": (cost_red / 100) if cost_red is not None else None,
                "avg_quality_retention": (qual_ret / 100) if qual_ret is not None else None,
                "total_cost_saved": (avgs['avg_base_cost'] - avgs['avg_cost']) * total if (avgs['avg_base_cost'] and avgs['avg_cost'] is not None) else 0
            }

    def get_model_distribution(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT selected_model, count(*) FROM experiments GROUP BY selected_model')
            return {row[0]: row[1] for row in cursor.fetchall()}

    # ── Benchmark Management Methods ──────────────────────────────────────────

    def save_benchmark_run(self, run_data: dict):
        """Register a new or resumed benchmark run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO benchmark_runs (
                    run_id, timestamp, execution_mode, dataset_version, total_prompts, policies, status, report_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_data["run_id"],
                run_data.get("timestamp", datetime.now().isoformat()),
                run_data.get("execution_mode", "demo"),
                run_data.get("dataset_version", "1.0.0"),
                run_data.get("total_prompts", 0),
                json.dumps(run_data.get("policies", [])),
                run_data.get("status", "running"),
                json.dumps(run_data.get("report_json")) if run_data.get("report_json") else None
            ))
            conn.commit()

    def update_benchmark_run_status(self, run_id: str, status: str, report_data: Optional[dict] = None):
        """Update run status and optional final report JSON."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE benchmark_runs
                SET status = ?, report_json = ?
                WHERE run_id = ?
            ''', (status, json.dumps(report_data) if report_data else None, run_id))
            conn.commit()

    def save_benchmark_result(self, res: dict):
        """Save a single prompt policy evaluation result with unique deduplication."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO benchmark_results (
                    run_id, prompt_id, category, policy, selected_model, model_id,
                    latency, prompt_tokens, completion_tokens, cost, quality_score,
                    eval_details, response, error, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                res["run_id"],
                res["prompt_id"],
                res["category"],
                res["policy"],
                res["selected_model"],
                res["model_id"],
                res["latency"],
                res.get("prompt_tokens", 0),
                res.get("completion_tokens", 0),
                res["cost"],
                res["quality_score"],
                res.get("eval_details", ""),
                res.get("response", ""),
                json.dumps(res.get("error")) if res.get("error") else None,
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_completed_benchmark_keys(self, run_id: str) -> Set[Tuple[str, str]]:
        """Return set of (prompt_id, policy) already evaluated for this run_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT prompt_id, policy FROM benchmark_results WHERE run_id = ?', (run_id,))
            return {(row[0], row[1]) for row in cursor.fetchall()}

    def get_benchmark_results_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        """Fetch all individual prompt results for a specific benchmark run."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM benchmark_results WHERE run_id = ? ORDER BY id ASC', (run_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_latest_benchmark_report(self) -> Optional[Dict[str, Any]]:
        """Fetch the most recently completed benchmark run report."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT report_json FROM benchmark_runs 
                WHERE status = 'completed' AND report_json IS NOT NULL 
                ORDER BY timestamp DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            if row and row['report_json']:
                return json.loads(row['report_json'])
            return None
