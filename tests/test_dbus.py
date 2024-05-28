import subprocess

def send_test_message(recipient_number, message, registered_number):
    try:
        # Send the test message using signal-cli command
        command = [
            'signal-cli',
            '-u',
            registered_number,  # Replace with your registered Signal phone number
            'send',
            '-m',
            message,
            recipient_number
        ]
        subprocess.run(command, check=True)
        print(f"Test message sent successfully to {recipient_number}")

    except subprocess.CalledProcessError as e:
        print(f"Error sending test message: {str(e)}")

# Usage example
recipient_number = '+491726947441'  # Replace with the recipient's phone number
test_message = 'This is a test message sent using signal-cli'
registered_number = '+4916099291575'

send_test_message(recipient_number, test_message, registered_number)