#!/usr/bin/env python3
# coding: utf-8

"""
Run this script with superuser rights ('sudo') to install the Signal CLI client.
"""

import os
import sys
import re
import subprocess
import logging
from pathlib import Path

def check_superuser():
    if os.geteuid() != 0:
        sys.exit("This script must be run with superuser privileges. Please run with 'sudo'.")

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def check_java():
    try:
        subprocess.run(['java', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Java is already installed.")
    except subprocess.CalledProcessError:
        logging.info("Java is not installed. Installing OpenJDK 11...")
        subprocess.run(['apt', 'update'], check=True)
        subprocess.run(['apt', 'install', '-y', 'openjdk-11-jre'], check=True)
        logging.info("Java installation completed.")

def check_git():
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.DEVNULL)
        logging.info("Git is already installed.")
    except subprocess.CalledProcessError:
        logging.info("Git is not installed. Installing Git...")
        subprocess.run(['apt', 'install', '-y', 'git'], check=True)
        logging.info("Git installation completed.")

def get_phone_number():
    while True:
        number = input("Enter the phone number associated with your Signal account (e.g., +1234567890): ").strip()
        if re.match(r'^\+\d{6,15}$', number):
            return number
        else:
            logging.warning("Invalid phone number format. Please try again.")

def get_signal_version():
    while True:
        version = input("Enter the Signal CLI version to install (e.g., 0.12.0): ").strip()
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
    except subprocess.CalledProcessError:
        sys.exit("Failed to download Signal CLI. Please check the version number and your internet connection.")

def install_signal_cli(version):
    tarball_path = Path(f"/tmp/signal-cli-{version}.tar.gz")
    install_dir = Path(f"/opt/signal-cli-{version}")
    bin_symlink = Path('/usr/local/bin/signal-cli')

    logging.info("Installing Signal CLI...")
    subprocess.run(['tar', 'xf', str(tarball_path), '-C', '/opt'], check=True)
    if bin_symlink.exists():
        bin_symlink.unlink()
    bin_symlink.symlink_to(install_dir / 'bin' / 'signal-cli')
    logging.info("Signal CLI installation completed.")

def configure_signal_cli(version, number):
    logging.info("Configuring Signal CLI as a system service...")
    temp_dir = Path('/tmp')
    subprocess.run(['git', 'clone', 'https://github.com/AsamK/signal-cli.git', str(temp_dir / 'signal-cli')], check=True)
    data_dir = temp_dir / 'signal-cli' / 'data'

    # Copy configuration files
    subprocess.run(['cp', str(data_dir / 'org.asamk.Signal.conf'), '/etc/dbus-1/system.d/'], check=True)
    subprocess.run(['cp', str(data_dir / 'org.asamk.Signal.service'), '/usr/share/dbus-1/system-services/'], check=True)
    subprocess.run(['cp', str(data_dir / 'signal-cli.service'), '/etc/systemd/system/'], check=True)

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
    result = subprocess.run(['signal-cli', '--config', '/var/lib/signal-cli', 'link', '-n', device_name], check=True, capture_output=True, text=True)
    link = result.stdout.strip()
    logging.info(f"Link generated: {link}")
    logging.info("Please generate a QR code from the link above and scan it using your Signal app.")

def finalize_installation():
    logging.info("Finalizing installation...")
    subprocess.run(['apt', 'install', '-y', 'libunixsocket-java'], check=True)
    subprocess.run(['cp', '/usr/lib/jni/libunix-java.so', '/lib'], check=True)
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'enable', 'signal-cli.service'], check=True)
    subprocess.run(['systemctl', 'reload', 'dbus.service'], check=True)
    subprocess.run(['systemctl', 'start', 'signal-cli.service'], check=True)
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
    check_superuser()
    logging.info("Welcome to the Signal CLI install wizard.")

    check_java()
    check_git()

    number = get_phone_number()
    version = get_signal_version()

    download_signal_cli(version)
    install_signal_cli(version)
    configure_signal_cli(version, number)

    install_mode = input("Will this computer be the master device for your Signal account? (Yes/No): ").strip().lower()
    if install_mode in ['yes', 'y']:
        register_signal(number)
    else:
        link_device()

    finalize_installation()
    send_test_message()
    logging.info("Installation and setup completed successfully.")

if __name__ == '__main__':
    main()