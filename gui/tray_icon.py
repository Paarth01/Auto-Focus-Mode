"""
System Tray Icon for Auto Focus Mode

Provides a system tray icon with menu options to control focus mode
without keeping the main window visible.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction


class FocusTrayIcon(QSystemTrayIcon):
    """
    System tray icon for Auto Focus Mode.
    
    Provides quick access to start/stop focus mode and exit the application.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setToolTip("Auto Focus Mode - Idle")
        self.setup_menu()
        self.activated.connect(self.on_tray_activated)
    
    def setup_menu(self):
        """Setup the context menu for the tray icon."""
        menu = QMenu()
        
        # Start action
        self.start_action = QAction("Start Focus Mode", self)
        self.start_action.triggered.connect(self.on_start)
        menu.addAction(self.start_action)
        
        # Stop action
        self.stop_action = QAction("Stop Focus Mode", self)
        self.stop_action.triggered.connect(self.on_stop)
        self.stop_action.setEnabled(False)
        menu.addAction(self.stop_action)
        
        menu.addSeparator()
        
        # Show window action
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show_window)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.on_exit)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def update_status(self, status: str):
        """
        Update the tray icon tooltip and menu based on status.
        
        Args:
            status: Current status ("Idle" or "Focus Active")
        """
        self.setToolTip(f"Auto Focus Mode - {status}")
        
        if status == "Focus Active":
            self.start_action.setEnabled(False)
            self.stop_action.setEnabled(True)
            # You could change icon here if you have different icons
        else:
            self.start_action.setEnabled(True)
            self.stop_action.setEnabled(False)
    
    def on_tray_activated(self, reason):
        """
        Handle tray icon activation (click).
        
        Args:
            reason: Activation reason (click, double-click, etc.)
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show the main window."""
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()
    
    def on_start(self):
        """Handle start focus mode from tray menu."""
        if self.parent_window:
            self.parent_window.on_start_clicked()
    
    def on_stop(self):
        """Handle stop focus mode from tray menu."""
        if self.parent_window:
            self.parent_window.on_stop_clicked()
    
    def on_exit(self):
        """Handle exit from tray menu."""
        if self.parent_window:
            if self.parent_window.controller.is_running:
                self.parent_window.controller.stop_focus()
            QApplication.quit()

