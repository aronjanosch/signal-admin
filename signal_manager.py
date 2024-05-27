import sys
import inquirer
import os
from dotenv import load_dotenv

from signal_dbus import SignalDBus
from signal_commands import SignalCommands

load_dotenv()
REGISTERED_NUMBER = os.getenv("REGISTERED_NUMBER")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--commands':
        use_dbus = False
        print("Running in command mode.")
    else:
        use_dbus = True
        print("Running in dbus mode.")

    registered_number = REGISTERED_NUMBER

    if use_dbus:
        signal_manager = SignalDBus(registered_number)
    else:
        signal_manager = SignalCommands(registered_number)

    while True:
        action = inquirer.list_input("Select an action:", choices=['Create Group', 'Update Group', 'Remove Group', 'Get Group ID', 'Exit'])

        if action == 'Create Group':
            group_name = inquirer.text("Enter the group name:")

            input_choice = inquirer.list_input("Select input method:", choices=['CSV File', 'Manual Input'])

            if input_choice == 'CSV File':
                csv_file_path = inquirer.path("Enter the CSV file path:")
                members = signal_manager.process_csv_file(csv_file_path)
            else:
                manual_input = inquirer.text("Enter phone numbers separated by commas:")
                members = [member.strip() for member in manual_input.split(',')]

            signal_manager.create_group(group_name, members)

        elif action == 'Update Group':
            groups = signal_manager.list_groups()
            if not groups:
                print("No groups found.")
                continue

            group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
            selected_group = inquirer.list_input("Select a group to update:", choices=group_choices)
            group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]
            print(group_id)
            update_action = inquirer.list_input("Select an update action:", choices=['Add Members', 'Remove Members'])

            input_choice = inquirer.list_input("Select input method:", choices=['CSV File', 'Manual Input'])

            if input_choice == 'CSV File':
                csv_file_path = inquirer.path("Enter the CSV file path:")
                members = signal_manager.process_csv_file(csv_file_path)
            else:
                manual_input = inquirer.text("Enter phone numbers, separated by commas:")
                members = [member.strip() for member in manual_input.split(',')]

            signal_manager.update_group(group_id, members, remove_members=(update_action == 'Remove Members'))

        elif action == 'Remove Group':
            groups = signal_manager.list_groups()
            if not groups:
                print("No groups found.")
                continue

            group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
            selected_group = inquirer.list_input("Select a group to remove:", choices=group_choices)
            group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]
            inquirer.text(group_id)

            confirm = inquirer.confirm(f"Are you sure you want to remove the group '{selected_group}'?")
            if confirm:
                signal_manager.remove_group(group_id)
                print(f"Group '{selected_group}' has been removed.")
            else:
                print("Group removal canceled.")

        elif action == 'Get Group ID':
            groups = signal_manager.list_groups()
            if not groups:
                print("No groups found.")
                continue

            group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
            selected_group = inquirer.list_input("Select a group to get the ID:", choices=group_choices)
            group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]

            print(f"Group ID for '{selected_group}': {group_id}")

        elif action == 'Exit':
            break

        print()  # Add a blank line for readability

if __name__ == '__main__':
    main()