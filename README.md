
A Signal administration tool written in python. It features a simple cli UI to create, delete and modify groups

# Signal Admin Tool

Welcome to the **Signal Admin Tool** setup repository. This repository contains scripts to install and update **Signal CLI**, which is required for the Signal Admin Tool—a Python application designed to manage and automate tasks on Signal messenger.

## Table of Contents

- [Signal Admin Tool](#signal-admin-tool)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Updating Signal CLI](#updating-signal-cli)
  - [Usage](#usage)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)

## Introduction

The **Signal Admin Tool** is a Python application that leverages **Signal CLI** to provide administrative functionalities for Signal messenger. This includes sending messages, managing groups, and automating communication tasks. The scripts in this repository help you set up and maintain the necessary environment to run the admin tool efficiently.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System**: Linux-based system (Ubuntu, Debian, etc.)
- **Python**: Version 3.6 or higher
- **Java Runtime Environment**: OpenJDK 11 or higher
- **Git**: For cloning repositories
- **Signal CLI**: Installed via the provided install script

## Installation

Follow these steps to install Signal CLI using the provided installation script.

### 1. Clone the Repository

```bash
git clone https://github.com/aronjanosch/signal-admin.git
cd signal-admin
```

### 2. Create and Activate a Virtual Environment

It’s recommended to use a Python virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Run the Install Script

Execute the installation script without sudo:
```bash
python scripts/install_signal_cli.py
```

**The script will:**

- Automatically fetch the latest version of Signal CLI.
- Prompt you to confirm or specify a different version.
- Install Signal CLI and its dependencies.
- Configure Signal CLI as a system service.
- Register your device or link it to an existing account.
- Send a test message to verify the installation.

**Notes**

- You may be prompted for your sudo password during the installation when the script needs elevated privileges.
- Ensure you have an active internet connection throughout the installation process.

## Updating Signal CLI

To update Signal CLI to the latest version, use the provided update script.

### 1. Run the Update Script
```bash
python scripts/update_signal_cli.py
```

The script will:

- Retrieve the latest Signal CLI version from GitHub.
- Prompt you to confirm the update.
- Download and install the new version.
- Update the system service configuration.
- Restart the Signal CLI service.

**Notes**
- Backup any important data before updating.
- The update script also requires internet access and may prompt for sudo privileges.

## Usage

After installing Signal CLI, you can use the Signal Admin Tool to manage your Signal account.

### Create .env file
Create an .env file with you registered number.

You can use this command and replace ```[Your Number]```
```bash
echo "REGISTERED_NUMBER=[Your Number]" > .env
```

Either run ```python3 signal-manager-py``` for an interactive UI or run ```python3 group-sync.py```for automated group creation and updates using the .csv files.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [AsamK](https://github.com/AsamK) for developing [Signal CLI](https://github.com/AsamK/signal-cli).
- The[ Signal Messenger](https://signal.org/) team for providing a secure messaging platform.
- Contributors and the open-source community for their valuable work.

For any issues or questions, please open an issue on GitHub or contact [*aron.wiederkehr@gmail.com*](aron.wiederkehr@gmail.com)

