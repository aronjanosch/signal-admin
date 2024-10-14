#!/usr/bin/env python3
# coding: utf-8

"""
Signal CLI Update Script

This script updates Signal CLI to the latest version by performing the following actions:
- Automatically retrieves the latest version from the official GitHub repository.
- Prompts the user to confirm the update.
- Downloads the new version.
- Unpacks the archive into the /opt directory.
- Updates the symbolic link in /usr/local/bin/.
- Updates the system service file if necessary.
- Reloads the system daemon and restarts the Signal CLI service.

Run this script with superuser privileges ('sudo').
"""

import os
import sys
import re
import subprocess
import logging
import requests
from pathlib import Path

def check_superuser():
    if os.geteuid() != 0:
        sys.exit("This script must be run with superuser privileges. Please run with 'sudo'.")

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_installed_version():
    try:
        result = subprocess.run(['signal-cli', '--version'], check=True, capture_output=True, text=True)
        installed_version = result.stdout.strip().split()[-1]
        return installed_version
    except subprocess.CalledProcessError:
        return None

def get_latest_version():
    logging.info("Retrieving the latest Signal CLI version from GitHub...")
    api_url = "https://api.github.com/repos/AsamK/signal-cli/releases/latest"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release['tag_name'].lstrip('v')
        logging.info(f"Latest version available: {latest_version}")
        return latest_version
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve the latest version: {e}")
        sys.exit("Exiting due to the above error.")

def prompt_for_update(installed_version, latest_version):
    if installed_version:
        logging.info(f"Currently installed version: {installed_version}")
    else:
        logging.info("Signal CLI is not currently installed or the version could not be determined.")
    choice = input(f"Do you want to update to the latest version {latest_version}? (Yes/No): ").strip().lower()
    if choice in ['yes', 'y']:
        return True
    else:
        logging.info("Update canceled by the user.")
        return False

def download_signal_cli(version):
    url = f"https://github.com/AsamK/signal-cli/releases/download/v{version}/signal-cli-{version}.tar.gz"
    temp_dir = Path('/tmp')
    tarball_path = temp_dir / f"signal-cli-{version}.tar.gz"
    logging.info(f"Downloading Signal CLI version {version}...")
    try:
        subprocess.run(['wget', url, '-O', str(tarball_path)], check=True)
        logging.info("Download completed.")
        return tarball_path
    except subprocess.CalledProcessError:
        sys.exit("Failed to download Signal CLI. Please check your internet connection.")

def unpack_signal_cli(version, tarball_path):
    install_dir = Path(f"/opt/signal-cli-{version}")
    logging.info("Unpacking Signal CLI...")
    try:
        subprocess.run(['tar', 'xf', str(tarball_path), '-C', '/opt'], check=True)
        logging.info(f"Signal CLI unpacked to {install_dir}.")
        return install_dir
    except subprocess.CalledProcessError:
        sys.exit("Failed to unpack the Signal CLI archive.")

def update_symbolic_link(install_dir):
    bin_symlink = Path('/usr/local/bin/signal-cli')
    logging.info("Updating symbolic link for signal-cli...")
    if bin_symlink.exists() or bin_symlink.is_symlink():
        bin_symlink.unlink()
    bin_symlink.symlink_to(install_dir / 'bin' / 'signal-cli')
    logging.info(f"Symbolic link updated to point to {install_dir / 'bin' / 'signal-cli'}.")

def update_service_file(version):
    service_file = Path('/etc/systemd/system/signal-cli.service')
    if not service_file.exists():
        logging.warning("Signal CLI service file does not exist. Skipping service file update.")
        return

    logging.info("Updating the system service file with the new version...")
    try:
        with service_file.open('r') as file:
            content = file.read()
        # Update the directory path to the new version
        content = re.sub(r'/opt/signal-cli-\d+\.\d+\.\d+', f'/opt/signal-cli-{version}', content)
        with service_file.open('w') as file:
            file.write(content)
        logging.info("Service file updated.")
    except Exception as e:
        logging.error(f"Failed to update the service file: {e}")
        sys.exit("Exiting due to the above error.")

def reload_and_restart_service():
    logging.info("Reloading system daemon and restarting Signal CLI service...")
    try:
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', 'restart', 'signal-cli.service'], check=True)
        logging.info("Signal CLI service restarted successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to reload or restart the service: {e}")
        sys.exit("Exiting due to the above error.")

def verify_update(version):
    logging.info("Verifying the Signal CLI update...")
    try:
        result = subprocess.run(['signal-cli', '--version'], check=True, capture_output=True, text=True)
        installed_version = result.stdout.strip().split()[-1]
        if installed_version == version:
            logging.info(f"Signal CLI successfully updated to version {version}.")
        else:
            logging.warning(f"Installed version ({installed_version}) does not match the expected version ({version}).")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to verify the Signal CLI version: {e}")
        sys.exit("Exiting due to the above error.")

def main():
    setup_logging()
    check_superuser()
    logging.info("Signal CLI Update Script")

    installed_version = get_installed_version()
    latest_version = get_latest_version()

    if not prompt_for_update(installed_version, latest_version):
        sys.exit()

    tarball_path = download_signal_cli(latest_version)
    install_dir = unpack_signal_cli(latest_version, tarball_path)
    update_symbolic_link(install_dir)
    update_service_file(latest_version)
    reload_and_restart_service()
    verify_update(latest_version)
    logging.info("Update process completed successfully.")

if __name__ == '__main__':
    main()