#!/usr/bin/env python3
# coding: utf-8

"""
Signal CLI Install Script

This script installs and configures Signal CLI on your system.
It also creates an .env file and sets up the necessary environment for the Signal Admin Tool.

Run this script without 'sudo'.
"""

import os
import sys
import re
import subprocess
import logging
import tempfile
import requests  # For fetching the latest version
from pathlib import Path

# Install required Python libraries in the virtual environment
def install_python_packages():
    required_packages = ['qrcode', 'Pillow', 'requests']
    for package in required_packages:
        try:
            __import__(package.lower())
        except ImportError:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)

# Call the function to install required packages
install_python_packages()

import qrcode
from PIL import Image

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def check_java():
    try:
        subprocess.run(['java', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Java is already installed.")
    except subprocess.CalledProcessError:
        logging.info("Java is not installed. Installing OpenJDK 11...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'openjdk-11-jre'], check=True)
        logging.info("Java installation completed.")

def check_git():
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.DEVNULL)
        logging.info("Git is already installed.")
    except subprocess.CalledProcessError:
        logging.info("Git is not installed. Installing Git...")
        subprocess.run(['sudo', 'apt', 'install', '-y', 'git'], check=True)
        logging.info("Git installation completed.")

def get_phone_number():
    while True:
        number = input("Enter the phone number associated with your Signal account (e.g., +1234567890): ").strip()
        if re.match(r'^\+\d{6,15}$', number):
            return number
        else:
            logging.warning("Invalid phone number format. Please try again.")

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

def get_signal_version():
    latest_version = get_latest_version()
    while True:
        version = input(f"Enter the Signal CLI version to install [Default: {latest_version}]: ").strip()
        if not version:
            version = latest_version
        if re.match(r'^\d+\.\d+\.\d+$', version):
            return version
        else:
            logging.warning("Invalid version format. Please try again.")

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
        sys.exit("Failed to download Signal CLI. Please check the version number and your internet connection.")

def install_signal_cli(version, tarball_path):
    install_dir = Path(f"/opt/signal-cli-{version}")
    bin_symlink = Path('/usr/local/bin/signal-cli')

    logging.info("Installing Signal CLI...")
    subprocess.run(['sudo', 'tar', 'xf', str(tarball_path), '-C', '/opt'], check=True)
    if bin_symlink.exists() or bin_symlink.is_symlink():
        subprocess.run(['sudo', 'rm', str(bin_symlink)], check=True)
    subprocess.run(['sudo', 'ln', '-sf', str(install_dir / 'bin' / 'signal-cli'), str(bin_symlink)], check=True)
    logging.info("Signal CLI installation completed.")

def configure_signal_cli(version, number):
    logging.info("Configuring Signal CLI as a system service...")

    # Use a unique temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        subprocess.run(['git', 'clone', 'https://github.com/AsamK/signal-cli.git', str(temp_path / 'signal-cli')], check=True)
        data_dir = temp_path / 'signal-cli' / 'data'

        # Copy configuration files
        subprocess.run(['sudo', 'cp', str(data_dir / 'org.asamk.Signal.conf'), '/etc/dbus-1/system.d/'], check=True)
        subprocess.run(['sudo', 'cp', str(data_dir / 'org.asamk.Signal.service'), '/usr/share/dbus-1/system-services/'], check=True)
        subprocess.run(['sudo', 'cp', str(data_dir / 'signal-cli.service'), '/etc/systemd/system/'], check=True)

    # Update the service file
    service_file = Path('/etc/systemd/system/signal-cli.service')
    with service_file.open('r') as file:
        content = file.read()
    content = content.replace('%dir%', f'/opt/signal-cli-{version}').replace('%number%', number)
    content = content.replace('User=signal-cli', 'User=root')
    with service_file.open('w') as file:
        file.write(content)

    # Update the D-Bus policy file
    policy_file = Path('/etc/dbus-1/system.d/org.asamk.Signal.conf')
    with policy_file.open('r') as file:
        content = file.read()
    content = content.replace('policy user="signal-cli"', 'policy user="root"')
    with policy_file.open('w') as file:
        file.write(content)

def create_env_files(number):
    logging.info("Creating .env file with the registered phone number...")
    env_file = Path('.env')
    with env_file.open('w') as file:
        file.write(f"REGISTERED_NUMBER={number}\n")
    logging.info(".env file created.")

    logging.info("Creating 'env' directory and copying templates...")
    env_dir = Path('env')
    env_dir.mkdir(exist_ok=True)

    templates_dir = Path('templates')
    if not templates_dir.exists():
        logging.warning("Templates directory does not exist. Skipping template copying.")
    else:
        for template_file in ['groups.csv', 'members.csv']:
            source = templates_dir / template_file
            destination = env_dir / template_file
            if source.exists():
                content = source.read_text()
                destination.write_text(content)
                logging.info(f"Copied {template_file} to 'env' directory.")
            else:
                logging.warning(f"Template {template_file} does not exist in 'templates' directory.")

def register_signal(number):
    logging.info("Registering this device as the master device for your Signal account.")
    can_receive_sms = input("Can this phone number receive SMS? (Yes/No): ").strip().lower()
    if can_receive_sms in ['yes', 'y']:
        subprocess.run(['signal-cli', '--config', '/var/lib/signal-cli', '-u', number, 'register'], check=True)
    else:
        subprocess.run(['signal-cli', '--config', '/var/lib/signal-cli', '-u', number, 'register', '--voice'], check=True)

    while True:
        verification_code = input("Enter the 6-digit verification code you received: ").strip()
        if re.match(r'^\d{6}$', verification_code):
            try:
                subprocess.run(['signal-cli', '--config', '/var/lib/signal-cli', '-u', number, 'verify', verification_code], check=True)
                logging.info("Verification successful.")
                break
            except subprocess.CalledProcessError:
                logging.warning("Verification failed. Please check the code and try again.")
        else:
            logging.warning("Invalid code format. Please enter a 6-digit code.")

def link_device():
    device_name = input("Enter a name for this device: ").strip()
    logging.info("Generating a link QR code...")

    try:
        # Start the signal-cli link command
        process = subprocess.Popen(
            ['signal-cli', '--config', '/var/lib/signal-cli', 'link', '-n', device_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        link = None

        # Read output line by line
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            logging.debug(f"signal-cli output: {line}")

            # Check if the line contains the link
            if line.startswith('tsdevice:/') or line.startswith('sgnl:/'):
                link = line
                logging.info("Link generated.")

                # Generate the QR code
                qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
                qr.add_data(link)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Display the QR code image
                img_path = '/tmp/signal_link_qr.png'
                img.save(img_path)
                logging.info("Displaying the QR code. Please scan it using your Signal app.")
                img.show()

        # Wait for the process to complete
        process.wait()

        # Check the return code
        if process.returncode == 0:
            logging.info("Device linked successfully.")
        else:
            logging.error("Linking failed. Please try again.")

    except Exception as e:
        logging.error(f"An error occurred while linking the device: {e}")
        sys.exit("Exiting due to the above error.")

def finalize_installation():
    logging.info("Finalizing installation...")
    subprocess.run(['sudo', 'apt', 'install', '-y', 'libunixsocket-java'], check=True)
    subprocess.run(['sudo', 'cp', '/usr/lib/jni/libunix-java.so', '/lib'], check=True)
    subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', 'signal-cli.service'], check=True)
    subprocess.run(['sudo', 'systemctl', 'reload', 'dbus.service'], check=True)
    subprocess.run(['sudo', 'systemctl', 'start', 'signal-cli.service'], check=True)
    logging.info("Signal CLI service started successfully.")

def send_test_message():
    while True:
        test_number = input("Enter a Signal-enabled phone number to send a test message: ").strip()
        if re.match(r'^\+\d{6,15}$', test_number):
            message = "Signal CLI installation is successful. This is a test message."
            try:
                subprocess.run([
                    'signal-cli', '--config', '/var/lib/signal-cli', '--dbus-system',
                    'send', '-m', message, test_number
                ], check=True)
                logging.info("Test message sent successfully.")
                break
            except subprocess.CalledProcessError:
                logging.warning("Failed to send test message. Please check the number and try again.")
        else:
            logging.warning("Invalid phone number format. Please try again.")

def main():
    setup_logging()
    logging.info("Welcome to the Signal CLI install wizard.")

    check_java()
    check_git()

    number = get_phone_number()
    version = get_signal_version()

    tarball_path = download_signal_cli(version)
    install_signal_cli(version, tarball_path)
    configure_signal_cli(version, number)

    install_mode = input("Will this computer be the master device for your Signal account? (Yes/No): ").strip().lower()
    if install_mode in ['yes', 'y']:
        register_signal(number)
    else:
        link_device()

    finalize_installation()
    create_env_files(number)
    send_test_message()
    logging.info("Installation and setup completed successfully.")

if __name__ == '__main__':
    main()