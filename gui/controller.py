"""
GUI Controller - Wrapper for Backend Functions

This module acts as a bridge between the PyQt6 GUI and the existing backend.
It safely imports and calls backend functions without modifying the core logic.

IMPORTANT: This is a GUI layer only. All business logic remains in the backend.
"""

import asyncio
import io
import queue
import sqlite3
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional

# Import backend functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    focus_daemon,
    block_websites,
    unblock_websites,
    apply_focus_policies,
    init_db,
    DB_FILE
)


class GuiLogStream(io.TextIOBase):
    """Tee-like stream that forwards writes to stdout/stderr and a queue."""

    def __init__(self, message_queue: queue.Queue, original_stream, stream_name: str):
        super().__init__()
        self._queue = message_queue
        self._original_stream = original_stream
        self._stream_name = stream_name
        self._buffer = ""
        self._lock = threading.Lock()

    def write(self, message: str) -> int:  # type: ignore[override]
        if not message:
            return 0

        with self._lock:
            self._original_stream.write(message)
            self._original_stream.flush()

            self._buffer += message
            while "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                self._queue.put((self._stream_name, line.rstrip("\r")))

        return len(message)

    def flush(self) -> None:  # type: ignore[override]
        with self._lock:
            self._original_stream.flush()
            if self._buffer:
                self._queue.put((self._stream_name, self._buffer.rstrip("\r")))
                self._buffer = ""


class FocusController:
    """
    Controller class that manages focus mode state and provides
    a synchronous interface for the GUI to interact with the backend.
    """
    
    def __init__(self):
        self.is_running = False
        self.daemon_thread: Optional[threading.Thread] = None
        self.daemon_loop: Optional[asyncio.AbstractEventLoop] = None
        self.daemon_task: Optional[asyncio.Task] = None
        self.stop_event = threading.Event()
        self.current_status = "Idle"
        self.log_queue: queue.Queue = queue.Queue()
        self._init_database()
    
    def _init_database(self):
        """Initialize the database if it doesn't exist."""
        try:
            init_db()
        except Exception as e:
            print(f"[GUI] Warning: Could not initialize database: {e}")
    
    def start_focus(self) -> bool:
        """
        Start the focus mode daemon in a separate thread.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.is_running:
            return False
        
        try:
            self.stop_event.clear()

            # Clear any leftover log messages before starting a new session
            try:
                while True:
                    self.log_queue.get_nowait()
            except queue.Empty:
                pass
            
            # Start the async daemon in a new thread
            def run_daemon():
                self.daemon_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.daemon_loop)

                original_stdout = sys.stdout
                original_stderr = sys.stderr
                gui_stdout = GuiLogStream(self.log_queue, original_stdout, "stdout")
                gui_stderr = GuiLogStream(self.log_queue, original_stderr, "stderr")
                sys.stdout = gui_stdout
                sys.stderr = gui_stderr
                try:
                    # Create a task that can be cancelled
                    self.daemon_task = self.daemon_loop.create_task(focus_daemon())
                    self.daemon_loop.run_until_complete(self.daemon_task)
                except asyncio.CancelledError:
                    print("[GUI] Daemon stopped")
                except Exception as e:
                    print(f"[GUI] Daemon error: {e}")
                finally:
                    gui_stdout.flush()
                    gui_stderr.flush()
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    # Clean up any pending tasks
                    pending = asyncio.all_tasks(self.daemon_loop)
                    for task in pending:
                        task.cancel()
                    self.daemon_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    self.daemon_loop.close()
                    self.daemon_loop = None
                    self.daemon_task = None
            
            self.daemon_thread = threading.Thread(target=run_daemon, daemon=True)
            self.daemon_thread.start()
            self.is_running = True
            self.current_status = "Focus Active"
            return True
        except Exception as e:
            print(f"[GUI] Failed to start focus mode: {e}")
            return False
    
    def stop_focus(self) -> bool:
        """
        Stop the focus mode daemon and clean up.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.is_running:
            return False
        
        try:
            # Signal stop
            self.stop_event.set()
            
            # Cancel the daemon task if it exists
            if self.daemon_loop and self.daemon_task:
                try:
                    # Schedule cancellation in the event loop
                    self.daemon_loop.call_soon_threadsafe(self.daemon_task.cancel)
                except Exception as e:
                    print(f"[GUI] Error cancelling task: {e}")
            
            # Clean up: unblock websites and restore policies
            try:
                unblock_websites()
                apply_focus_policies("productive")
            except Exception as e:
                print(f"[GUI] Warning: Error during cleanup: {e}")
            
            self.is_running = False
            self.current_status = "Idle"
            
            # Wait for thread to finish (with timeout)
            if self.daemon_thread and self.daemon_thread.is_alive():
                self.daemon_thread.join(timeout=3.0)
            
            return True
        except Exception as e:
            print(f"[GUI] Failed to stop focus mode: {e}")
            self.is_running = False
            self.current_status = "Idle"
            return False
    
    def get_status(self) -> str:
        """
        Get the current focus mode status.
        
        Returns:
            str: Current status ("Idle" or "Focus Active")
        """
        return self.current_status
    
    def get_log_queue(self) -> queue.Queue:
        """Return the queue that receives stdout/stderr lines."""
        return self.log_queue

    def get_recent_sessions(self, limit: int = 50) -> List[Tuple[str, str, float]]:
        """
        Retrieve recent focus sessions from the database.
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of tuples: (app_name, mode/category, duration_minutes)
            Note: Duration is estimated as time until next session or current time
        """
        sessions = []
        try:
            # Ensure DB_FILE is resolved as a Path object
            db_path = Path(DB_FILE) if not isinstance(DB_FILE, Path) else DB_FILE
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Try focus_log table first (from main.py)
            try:
                cursor.execute("""
                    SELECT app_name, mode, timestamp 
                    FROM focus_log 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                
                # Calculate duration: time until next session (or 0 for most recent)
                if rows:
                    current_time = datetime.now()
                    for i, (app_name, mode, timestamp) in enumerate(rows):
                        try:
                            session_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                            # Duration is time until next session, or until now for the most recent
                            if i == 0:  # Most recent session
                                duration = (current_time - session_time).total_seconds() / 60.0
                            else:
                                next_time = datetime.strptime(rows[i-1][2], "%Y-%m-%d %H:%M:%S")
                                duration = (next_time - session_time).total_seconds() / 60.0
                            # Only show positive durations
                            if duration > 0:
                                sessions.append((app_name, mode, duration))
                        except (ValueError, IndexError):
                            sessions.append((app_name, mode, 0.0))
            except sqlite3.OperationalError:
                # Try focus_sessions table (from data_logger.py)
                cursor.execute("""
                    SELECT app_name, category, timestamp 
                    FROM focus_sessions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                
                if rows:
                    current_time = datetime.now()
                    for i, (app_name, category, timestamp) in enumerate(rows):
                        try:
                            if isinstance(timestamp, str):
                                session_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                            else:
                                session_time = timestamp
                            
                            # Duration is time until next session, or until now for the most recent
                            if i == 0:  # Most recent session
                                duration = (current_time - session_time).total_seconds() / 60.0
                            else:
                                prev_timestamp = rows[i-1][2]
                                if isinstance(prev_timestamp, str):
                                    next_time = datetime.strptime(prev_timestamp, "%Y-%m-%d %H:%M:%S")
                                else:
                                    next_time = prev_timestamp
                                duration = (next_time - session_time).total_seconds() / 60.0
                            
                            # Only show positive durations
                            if duration > 0:
                                sessions.append((app_name, category, duration))
                        except (ValueError, TypeError, IndexError):
                            sessions.append((app_name, category, 0.0))
            
            conn.close()
        except Exception as e:
            print(f"[GUI] Error fetching sessions: {e}")
        
        # Return sessions (newest first for display)
        return sessions
    
    def get_session_stats(self) -> dict:
        """
        Get statistics about focus sessions.
        
        Returns:
            dict: Statistics including total sessions, total time, etc.
        """
        sessions = self.get_recent_sessions(limit=1000)
        total_time = sum(duration for _, _, duration in sessions)
        productive_count = sum(1 for _, mode, _ in sessions if mode == "productive")
        distracted_count = sum(1 for _, mode, _ in sessions if mode == "distracted")
        
        return {
            "total_sessions": len(sessions),
            "total_time_minutes": total_time,
            "productive_count": productive_count,
            "distracted_count": distracted_count
        }

