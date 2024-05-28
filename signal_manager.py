import sys
import inquirer
import os
from dotenv import load_dotenv

from signal_dbus import SignalDBus
from signal_commands import SignalCommands

load_dotenv()
REGISTERED_NUMBER = os.getenv("REGISTERED_NUMBER")

def create_group(signal_manager):
    group_name = inquirer.text("Enter the group name:")
    input_choice = inquirer.list_input("Select input method:", choices=['CSV File', 'Manual Input'])

    if input_choice == 'CSV File':
        csv_file_path = inquirer.path("Enter the CSV file path:")
        members = signal_manager.process_csv_file(csv_file_path)
    else:
        manual_input = inquirer.text("Enter phone numbers separated by commas:")
        if manual_input:
            members = [member.strip() for member in manual_input.split(',')]
        else:
            members = []

    signal_manager.create_group(group_name, members)

def update_group(signal_manager):
    groups = signal_manager.list_groups()
    if not groups:
        print("No groups found.")
        return

    group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
    selected_group = inquirer.list_input("Select a group to update:", choices=group_choices)
    group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]

    update_action = inquirer.list_input("Select an update action:", choices=['Add Members', 'Remove Members'])
    input_choice = inquirer.list_input("Select input method:", choices=['CSV File', 'Manual Input'])

    if input_choice == 'CSV File':
        csv_file_path = inquirer.path("Enter the CSV file path:")
        members = signal_manager.process_csv_file(csv_file_path)
    else:
        manual_input = inquirer.text("Enter phone numbers, separated by commas:")
        members = [member.strip() for member in manual_input.split(',')]

    signal_manager.update_group(group_id, members, remove_members=(update_action == 'Remove Members'))

def remove_group(signal_manager):
    groups = signal_manager.list_groups()
    if not groups:
        print("No groups found.")
        return

    group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
    selected_group = inquirer.list_input("Select a group to remove:", choices=group_choices)
    group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]

    confirm = inquirer.confirm(f"Are you sure you want to remove the group '{selected_group}'?")
    if confirm:
        signal_manager.remove_group(group_id)
        print(f"Group '{selected_group}' has been removed.")
    else:
        print("Group removal canceled.")

def get_group_id(signal_manager):
    groups = signal_manager.list_groups()
    if not groups:
        print("No groups found.")
        return

    group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
    selected_group = inquirer.list_input("Select a group to get the ID:", choices=group_choices)
    group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]

    print(f"Group ID for '{selected_group}': {group_id}")

def get_group_property(signal_manager):
    groups = signal_manager.list_groups()
    if not groups:
        print("No groups found.")
        return

    group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
    selected_group = inquirer.list_input("Select a group to get property:", choices=group_choices)
    group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]

    property_name = inquirer.text("Enter the property name:")

    value = signal_manager.get_group_property(group_id, property_name)
    if value is not None:
        print(f"Property '{property_name}' value: {value}")

def set_group_property(signal_manager):
    groups = signal_manager.list_groups()
    if not groups:
        print("No groups found.")
        return

    group_choices = [f"{group_name}" for group_id, group_name in groups if group_name]
    selected_group = inquirer.list_input("Select a group to set property:", choices=group_choices)
    group_id = [group_id for (group_id, group_name) in groups if group_name == selected_group][0]

    property_name = inquirer.text("Enter the property name:")
    property_value = inquirer.text("Enter the property value:")

    signal_manager.set_group_property(group_id, property_name, property_value)
    print(f"Property '{property_name}' set to '{property_value}' for group '{selected_group}'.")


def utils_menu(signal_manager):
    while True:
        action = inquirer.list_input("Select a utility action:", choices=['Get Group Property', 'Set Group Property', 'Back'])

        if action == 'Get Group Property':
            get_group_property(signal_manager)
        elif action == 'Set Group Property':
            set_group_property(signal_manager)
        elif action == 'Back':
            break

def main_menu(signal_manager):
    while True:
        action = inquirer.list_input("Select an action:", choices=['Create Group', 'Update Group', 'Remove Group', 'Get Group ID', 'Utils', 'Exit'])

        if action == 'Create Group':
            create_group(signal_manager)
        elif action == 'Update Group':
            update_group(signal_manager)
        elif action == 'Remove Group':
            remove_group(signal_manager)
        elif action == 'Get Group ID':
            get_group_id(signal_manager)
        elif action == 'Utils':
            utils_menu(signal_manager)
        elif action == 'Exit':
            break

        print()  # Add a blank line for readability

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

    main_menu(signal_manager)

if __name__ == '__main__':
    main()