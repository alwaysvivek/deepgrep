import sqlite3, json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple
from decouple import config

# Configure logging
logger = logging.getLogger(__name__)

# Load configuration from environment variables
DB_PATH = Path(config('DB_PATH', default='~/.grepify_history.db')).expanduser()
MAX_HISTORY = config('MAX_HISTORY', default=200, cast=int)

class SearchHistoryDB:
    """SQLite-backed search history logger."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        logger.info(f"Initializing search history database at {self.db_path}")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    match_count INTEGER,
                    files TEXT
                );
            """)
        logger.info("Database initialized successfully")

    def log_search(self, pattern: str, match_count: int, files: List[str]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO search_logs (pattern, timestamp, match_count, files) VALUES (?, ?, ?, ?)",
                (pattern, datetime.now(timezone.utc).isoformat(), match_count, json.dumps(files)),
            )
            # Cleanup old records
            result = conn.execute("""
                DELETE FROM search_logs WHERE id NOT IN (
                    SELECT id FROM search_logs ORDER BY id DESC LIMIT ?
                );
            """, (MAX_HISTORY,))
            deleted_count = result.rowcount
            conn.commit()
        logger.info(f"Logged search: pattern='{pattern}', matches={match_count}, files={len(files)}")
        if deleted_count > 0:
            logger.debug(f"Cleaned up {deleted_count} old records")

    def get_recent(self, limit: int = 5) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT pattern, timestamp, match_count, files FROM search_logs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()

    def get_top_patterns(self, limit: int = 5) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("""
                SELECT pattern, COUNT(*) as count
                FROM search_logs
                GROUP BY pattern
                ORDER BY count DESC
                LIMIT ?;
            """, (limit,)).fetchall()

    def list_all(self, limit: int = None) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT pattern, timestamp, match_count, files FROM search_logs ORDER BY id DESC"
            ).fetchall()

    def export_to_json(self, file_path: Path) -> int:
        rows = self.list_all()
        data = [
            {"pattern": r[0], "timestamp": r[1], "match_count": r[2], "files": json.loads(r[3])}
            for r in rows
        ]
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"Exported {len(data)} search records to {file_path}")
        return len(data)

    def import_from_json(self, file_path: Path) -> int:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        with sqlite3.connect(self.db_path) as conn:
            for entry in data:
                ts = entry.get("timestamp")
                if ts is None:
                    ts = datetime.now(timezone.utc).isoformat()
                conn.execute(
                    "INSERT INTO search_logs (pattern, timestamp, match_count, files) VALUES (?, ?, ?, ?)",
                    (
                        entry["pattern"],
                        ts,
                        entry.get("match_count", 0),
                        json.dumps(entry.get("files", [])),
                    ),
                )
            conn.execute("""
                DELETE FROM search_logs WHERE id NOT IN (
                    SELECT id FROM search_logs ORDER BY id DESC LIMIT ?
                );
            """, (MAX_HISTORY,))
            conn.commit()
        logger.info(f"Imported {len(data)} search records from {file_path}")
        return len(data)