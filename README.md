# signal-admin
A Signal administration tool written in python. It features a simple cli UI to create, delete and modify groups


## Install
1. Clone the repository

```
git clone https://github.com/aronjanosch/signal-admin.git
```

2. Install dependencies
- Install Java Ubuntu 22.04: ```sudo apt install openjdk-21-jre```
- Install Signal CLI with the installer script use sudo!
```
sudo python3 InstallSignalEN.py
```

3. install python Dependencies with venv or break-system-packages (at your own risk)

```
pip install -r requirements.txt --break-system-packages
```

## Usage

Either run ```python3 signal-manager-py``` for an interactive UI or run ```python3 group-sync.py```for automated group creation and updates using the .csv files.
