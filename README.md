# Auto-Focus-Mode

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  
[![GitHub issues](https://img.shields.io/github/issues/Paarth01/Auto-Focus-Mode)](https://github.com/Paarth01/Auto-Focus-Mode/issues)  
[![GitHub forks](https://img.shields.io/github/forks/Paarth01/Auto-Focus-Mode)](https://github.com/Paarth01/Auto-Focus-Mode/network)  
[![GitHub stars](https://img.shields.io/github/stars/Paarth01/Auto-Focus-Mode)](https://github.com/Paarth01/Auto-Focus-Mode/stargazers)  

Auto-Focus-Mode is an OS-level productivity enhancement tool designed to help users maintain focus by automatically managing distractions, notifications, and system settings while working or studying. It is built primarily for Ubuntu/Linux systems but can be extended for other platforms.

---

## 📌 Table of Contents

- [Overview](#-overview)  
- [Features](#-features)  
- [Installation](#-installation)  
- [Usage](#-usage)  
- [Configuration](#-configuration)    
- [Development](#-development)  
- [Roadmap](#-roadmap)  
- [Contributing](#-contributing)  
- [License](#-license)  
- [References](#-references)  

---

## 📝 Overview

Auto-Focus-Mode improves productivity by:

- Blocking distracting websites.  
- Silencing notifications automatically.  
- Muting/unmuting system audio.  
- Toggling Do Not Disturb mode in GNOME.  
- Logging focus sessions for analysis.

It is ideal for developers, students, or anyone who needs uninterrupted focus time.

---

## 🚀 Features

- **Automatic Focus Activation**: Detects active productive apps or scheduled times and activates focus mode.  
- **Website Blocking**: Temporarily blocks distracting websites via `/etc/hosts`.  
- **Notification Management**: Silences system notifications to minimize distractions.  
- **Audio Controls**: Automatically mutes or unmutes system audio.  
- **Do Not Disturb**: Toggles GNOME Do Not Disturb mode.  
- **Custom Configuration**: Users can edit `config.json` to adjust behavior, exceptions, and blocked websites.  
- **Activity Logging**: Records focus sessions in a lightweight SQLite database.  

---

## 🛠️ Installation

### Prerequisites

- Python 3.6 or higher  
- Ubuntu/Linux system (requires `sudo` for some operations)  
- Optional: `pip` for dependency management  

### Steps

1. Clone the repository:

```bash
git clone https://github.com/Paarth01/Auto-Focus-Mode.git
cd Auto-Focus-Mode
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
sudo python main.py
```

---

## ⚙️ Usage

- Start the app:
```bash
python main.py
```
- The tool automatically detects active productive apps and toggles focus mode.
- Customize behavior by editing config.json:
  - Add/remove apps to monitor
  - Specify websites to block
  - Adjust notification and audio behavior
- Stop focus mode manually via Ctrl+C or by closing the terminal running the script.
