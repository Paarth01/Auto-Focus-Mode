# Auto Focus Mode

An intelligent focus management system that automatically detects distracting applications and enforces focus policies to help you stay productive.

## Features

- **Automatic Activity Detection**: Monitors active applications and categorizes them as productive or distracting
- **Website Blocking**: Blocks distracting websites by modifying the hosts file
- **System Policy Enforcement**: Adjusts system settings (dock, notifications, audio) based on focus state
- **Session Logging**: Tracks focus sessions in SQLite database
- **Graphical User Interface**: Modern PyQt6-based GUI for easy control
- **System Tray Integration**: Minimize to system tray for background operation

## Installation

### Prerequisites

- Python 3.8 or higher
- Ubuntu with Xorg display server
- Required system tools: `xdotool`, `xprop` (for activity detection)
- Required Python packages: `psutil`, `pyyaml`, `PyQt6`

### Setup

1. Clone or navigate to the project directory:
```bash
cd auto-focus-mode
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install psutil pyyaml PyQt6
```

4. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get install xdotool x11-utils libxcb-cursor0
```

**Note**: The `libxcb-cursor0` package is required for PyQt6 to work with Xorg. If you encounter Qt platform plugin errors, make sure this package is installed.

## Usage

### Starting Auto Focus Mode

**Default behavior (with GUI):**
```bash
python3 main.py
```

This will:
1. Launch the GUI automatically (if PyQt6 is installed)
2. Automatically start the focus daemon
3. Allow you to control focus mode through the GUI

**CLI-only mode (without GUI):**
```bash
python3 main.py --no-gui
```

This runs the daemon directly in the terminal. Press `Ctrl+C` to stop.

**Note**: Some operations (like blocking websites) require sudo privileges. You may need to run with:
```bash
sudo python3 main.py
```

### Graphical User Interface

The GUI launches automatically when you run `python3 main.py`. 

**Manual GUI launch:**
```bash
python3 -m gui.gui_main
```

**Manual GUI launch with auto-start:**
```bash
python3 -m gui.gui_main --auto-start
```

This will automatically start the focus daemon when the GUI opens.

#### GUI Features

- **Status Display**: Shows current focus mode state ("Idle" or "Focus Active")
- **Start/Stop Buttons**: Control focus mode with a single click
- **Session Logs**: View recent focus sessions in a table
- **Refresh Logs**: Update the session log display
- **System Tray**: Minimize to system tray for background operation

#### GUI Components

1. **Main Window**
   - Status label showing current state
   - Start/Stop/Refresh buttons
   - Session log table with app name, mode, and duration

2. **System Tray Icon** (if available)
   - Right-click for context menu
   - Quick access to start/stop focus mode
   - Show/hide main window
   - Exit application

## Configuration

### Application Lists

Edit `config.yaml` to customize productive and distracting applications:

```yaml
productive_apps:
  - code
  - libreoffice
  - gedit
  - google-chrome

distracting_apps:
  - youtube
  - whatsapp
  - instagram
  - spotify
  - discord
  - firefox
```

### Blocked Websites

Edit `blocked_sites.txt` to add websites to block during focus mode:
```
youtube.com
www.youtube.com
facebook.com
www.facebook.com
```

## Architecture

### Backend (Core Functionality)

The backend consists of:
- `main.py`: Main daemon loop and core functions
- `modules/activity_detection.py`: Detects active applications
- `modules/data_logger.py`: Database operations for session logging
- `modules/focus_orchestrator.py`: Applies system policies
- `modules/policy_engine.py`: Loads and evaluates focus policies

### GUI Layer

The GUI is a separate layer that interacts with the backend:
- `gui/controller.py`: Wraps backend functions for GUI use
- `gui/gui_main.py`: Main window and application entry point
- `gui/tray_icon.py`: System tray icon implementation
- `gui/style.qss`: Stylesheet for modern UI appearance

**Important**: The GUI does not modify any backend code. It imports and calls existing functions, maintaining separation of concerns.

## How the GUI Interacts with the Backend

1. **Controller Pattern**: The `FocusController` class in `gui/controller.py` acts as a bridge between the GUI and backend:
   - Wraps async backend functions in a synchronous interface
   - Manages the focus daemon in a separate thread
   - Provides methods like `start_focus()`, `stop_focus()`, and `get_recent_sessions()`

2. **Threading**: The async `focus_daemon()` runs in a separate thread to avoid blocking the GUI event loop

3. **Database Access**: The GUI queries the SQLite database directly to display session logs

4. **State Management**: The controller maintains focus state and provides status updates to the GUI

## Extending the GUI

### Adding New UI Components

To add new components (e.g., charts, settings panel):

1. **Add to Main Window** (`gui/gui_main.py`):
   ```python
   # In init_ui() method
   chart_widget = QChartView()  # Example
   layout.addWidget(chart_widget)
   ```

2. **Add Controller Methods** (`gui/controller.py`):
   ```python
   def get_chart_data(self):
       # Fetch and process data
       return processed_data
   ```

3. **Update Styles** (`gui/style.qss`):
   ```css
   QChartView {
       background-color: white;
       border-radius: 4px;
   }
   ```

### Example: Adding a Statistics Panel

1. Create a new method in `FocusController`:
   ```python
   def get_daily_stats(self):
       # Query database for daily statistics
       return stats_dict
   ```

2. Add UI component in `gui_main.py`:
   ```python
   stats_label = QLabel()
   stats = self.controller.get_daily_stats()
   stats_label.setText(f"Today: {stats['total_time']} minutes")
   ```

3. Style in `style.qss`:
   ```css
   QLabel#statsLabel {
       font-size: 16px;
       font-weight: bold;
   }
   ```

### Example: Adding Settings Dialog

1. Create `gui/settings_dialog.py`:
   ```python
   class SettingsDialog(QDialog):
       def __init__(self, parent=None):
           super().__init__(parent)
           # Add settings UI
   ```

2. Import and use in `gui_main.py`:
   ```python
   from gui.settings_dialog import SettingsDialog
   
   def show_settings(self):
       dialog = SettingsDialog(self)
       dialog.exec()
   ```

## Troubleshooting

### GUI Won't Start

**Error: "Could not load the Qt platform plugin 'xcb'"**

This error occurs when the required system library is missing. Install it with:
```bash
sudo apt-get install libxcb-cursor0
```

**Other common issues:**

- Ensure PyQt6 is installed: `pip install PyQt6`
- Check Xorg is running: `echo $XDG_SESSION_TYPE` should output `x11`
- Verify Python version: `python3 --version` (3.8+)
- Make sure you're using the virtual environment: `source venv/bin/activate`
- If using Wayland, switch to Xorg or use the CLI interface instead

### Focus Mode Not Working

- Check if daemon is running (look for process)
- Verify system tools are installed: `which xdotool xprop`
- Check permissions for `/etc/hosts` modification (may need sudo)
- Review console output for error messages

### Database Issues

- Ensure `focus_db.sqlite` is writable
- Check database schema matches expected format
- Try deleting database file to reset (will lose logs)

## Development

### Project Structure

```
auto-focus-mode/
├── main.py                 # Backend entry point
├── config.yaml            # Configuration file
├── blocked_sites.txt      # Websites to block
├── focus_db.sqlite        # Session database
├── modules/               # Backend modules
│   ├── activity_detection.py
│   ├── data_logger.py
│   ├── focus_orchestrator.py
│   └── policy_engine.py
└── gui/                   # GUI layer
    ├── __init__.py
    ├── gui_main.py        # Main window
    ├── controller.py      # Backend wrapper
    ├── tray_icon.py       # System tray
    └── style.qss          # Stylesheet
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all classes and functions
- Keep GUI and backend code separate
