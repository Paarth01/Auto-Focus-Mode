"""
GUI Main Entry Point

This is the main entry point for the PyQt6-based GUI layer.
Run with: python3 -m gui.gui_main

The GUI provides a visual interface to control the Auto Focus Mode backend
without modifying any existing backend code.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSystemTrayIcon, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

import queue

from gui.controller import FocusController
from gui.tray_icon import FocusTrayIcon


class FocusMainWindow(QMainWindow):
    """
    Main window for Auto Focus Mode GUI.
    
    This window displays:
    - Current focus status
    - Start/Stop buttons
    - Refresh logs button
    - Table showing recent sessions
    """
    
    def __init__(self, auto_start=False):
        super().__init__()
        self.controller = FocusController()
        self.tray_icon = None
        self.auto_start = auto_start
        self.log_queue = self.controller.get_log_queue()
        self.init_ui()
        self.setup_timer()
        
        # Auto-start focus mode if requested
        if auto_start:
            QTimer.singleShot(500, self.auto_start_focus)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Auto Focus Mode")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Status section
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.status_value = QLabel("Idle")
        self.status_value.setStyleSheet("font-size: 14px; color: #666;")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.start_button = QPushButton("Start Focus Mode")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self.on_start_clicked)
        
        self.stop_button = QPushButton("Stop Focus Mode")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        
        self.refresh_button = QPushButton("Refresh Logs")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_logs)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Logs table section
        logs_label = QLabel("Recent Sessions:")
        logs_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(logs_label)
        
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels(["App Name", "Mode", "Duration (min)"])
        self.logs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.logs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.logs_table)
        
        # Terminal output section
        output_label = QLabel("Daemon Output:")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(output_label)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumBlockCount(1000)
        self.log_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_output.setStyleSheet("font-family: 'Courier New', monospace; font-size: 12px;")
        layout.addWidget(self.log_output)

        # Load initial logs
        self.refresh_logs()
    
    def setup_timer(self):
        """Setup timer to periodically update status."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second

        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.drain_log_queue)
        self.log_timer.start(250)
    
    def auto_start_focus(self):
        """Automatically start focus mode when GUI launches."""
        if not self.controller.is_running:
            self.on_start_clicked()
    
    def update_status(self):
        """Update the status label based on controller state."""
        status = self.controller.get_status()
        self.status_value.setText(status)
        
        if status == "Focus Active":
            self.status_value.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.status_value.setStyleSheet("font-size: 14px; color: #666;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        
        # Update tray icon if it exists
        if self.tray_icon:
            self.tray_icon.update_status(status)

    def drain_log_queue(self):
        """Append any new stdout/stderr lines to the log output widget."""
        updated = False
        while True:
            try:
                stream_name, line = self.log_queue.get_nowait()
            except queue.Empty:
                break

            if stream_name == "stderr" and line:
                display_line = f"[STDERR] {line}"
            else:
                display_line = line

            self.log_output.appendPlainText(display_line)
            updated = True

        if updated:
            scrollbar = self.log_output.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def on_start_clicked(self):
        """Handle start focus mode button click."""
        if self.controller.start_focus():
            QMessageBox.information(self, "Success", "Focus mode started successfully!")
            self.update_status()
        else:
            QMessageBox.warning(self, "Error", "Failed to start focus mode. It may already be running.")
    
    def on_stop_clicked(self):
        """Handle stop focus mode button click."""
        if self.controller.stop_focus():
            QMessageBox.information(self, "Success", "Focus mode stopped successfully!")
            self.update_status()
        else:
            QMessageBox.warning(self, "Error", "Failed to stop focus mode.")
    
    def refresh_logs(self):
        """Refresh the logs table with recent sessions."""
        sessions = self.controller.get_recent_sessions(limit=50)
        self.logs_table.setRowCount(len(sessions))
        
        for row, (app_name, mode, duration) in enumerate(sessions):
            self.logs_table.setItem(row, 0, QTableWidgetItem(app_name))
            self.logs_table.setItem(row, 1, QTableWidgetItem(mode))
            self.logs_table.setItem(row, 2, QTableWidgetItem(f"{duration:.2f}"))
            
            # Color code based on mode
            if mode == "productive":
                self.logs_table.item(row, 1).setForeground(Qt.GlobalColor.darkGreen)
            elif mode == "distracted":
                self.logs_table.item(row, 1).setForeground(Qt.GlobalColor.red)
    
    def setup_tray_icon(self):
        """Setup system tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = FocusTrayIcon(self)
            self.tray_icon.show()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.tray_icon and self.tray_icon.isVisible():
            QMessageBox.information(
                self,
                "Auto Focus Mode",
                "The application will continue to run in the system tray. "
                "To quit, choose 'Exit' from the tray icon menu."
            )
            self.hide()
            event.ignore()
        else:
            if self.controller.is_running:
                reply = QMessageBox.question(
                    self,
                    "Confirm Exit",
                    "Focus mode is currently active. Do you want to stop it and exit?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.controller.stop_focus()
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()


def main():
    """Main entry point for the GUI application."""
    # Check if running on Xorg
    import os
    if os.environ.get("XDG_SESSION_TYPE") != "x11":
        print("[WARNING] This GUI is designed for Xorg. You may experience issues on Wayland.")
    
    # Check for auto-start flag
    auto_start = "--auto-start" in sys.argv or os.environ.get("AUTO_FOCUS_START") == "1"
    
    # Check for required Qt dependencies
    try:
        app = QApplication(sys.argv)
    except Exception as e:
        print(f"[ERROR] Failed to initialize Qt application: {e}")
        print("\n[SOLUTION] Please install required system dependencies:")
        print("  sudo apt-get install libxcb-cursor0")
        print("\nIf the issue persists, ensure you're running on Xorg (not Wayland).")
        sys.exit(1)
    
    app.setApplicationName("Auto Focus Mode")
    
    # Load stylesheet if available
    style_path = Path(__file__).parent / "style.qss"
    if style_path.exists():
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    
    window = FocusMainWindow(auto_start=auto_start)
    
    # Setup tray icon if available
    if QSystemTrayIcon.isSystemTrayAvailable():
        window.setup_tray_icon()
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

