import csv
import os

from dotenv import load_dotenv
from signal_dbus import SignalDBus

load_dotenv()
REGISTERED_NUMBER = os.getenv("REGISTERED_NUMBER")


def create_groups_from_csv(signal_dbus, group_csv_file_path, groups_created_file_path):
    """
    Create Signal groups from a CSV file.

    Args:
        signal_dbus (SignalDBus): An instance of the SignalDBus class.
        group_csv_file_path (str): Path to the CSV file containing group information.
        groups_created_file_path (str): Path to the CSV file containing created group information.
    """
    with open(group_csv_file_path, 'r', encoding='UTF-8') as group_csv_file:
        reader = csv.DictReader(group_csv_file)
        rows = list(reader)

    existing_group_names = get_existing_group_names(groups_created_file_path)

    created_rows = []
    for row in rows:
        group_name = row['Group Name']
        group_description = row['Group Description']
        permission_add_members = row['PermissionAddMembers']
        permission_edit_details = row['PermissionEditDetails']
        permission_send_messages = row['PermissionSendMessages']
        
        if group_name not in existing_group_names:
            # Create the group if it doesn't exist and add it to the groups_created.csv file
            group_id = signal_dbus.create_group(group_name, [])
            signal_dbus.set_group_property(group_id, 'Description', group_description)
            signal_dbus.set_group_property(group_id, 'PermissionAddMembers', permission_add_members)
            signal_dbus.set_group_property(group_id, 'PermissionEditDetails', permission_edit_details)
            signal_dbus.set_group_property(group_id, 'PermissionSendMessages', permission_send_messages)
            created_rows.append({'Group ID': str(group_id), 'Group Name': group_name})
            print(f"Created group: {group_name}")
        else:
            print(f"Group '{group_name}' already exists. If this is an error, modify the groups_created.csv file.")

    # Append the created groups to the groups_created.csv file
    with open(groups_created_file_path, 'a', encoding='UTF-8', newline='') as groups_created_file:
        fieldnames = ['Group ID', 'Group Name']
        writer = csv.DictWriter(groups_created_file, fieldnames=fieldnames)
        writer.writerows(created_rows)


def get_existing_group_names(groups_created_file_path):
    """
    Retrieve the existing group names from the groups_created.csv file.

    Args:
        groups_created_file_path (str): Path to the CSV file containing created group information.

    Returns:
        set: A set of existing group names.
    """
    existing_group_names = set()
    if os.path.exists(groups_created_file_path):
        with open(groups_created_file_path, 'r', encoding='UTF-8') as groups_created_file:
            reader = csv.DictReader(groups_created_file)
            for row in reader:
                existing_group_names.add(row['Group Name'])
    return existing_group_names


def get_group_id_by_name(groups_created_file_path, group_name):
    """
    Retrieve the group ID based on the group name.

    Args:
        groups_created_file_path (str): Path to the CSV file containing created group information.
        group_name (str): The group name.

    Returns:
        list: The group ID as a list of integers.
    """
    with open(groups_created_file_path, 'r', encoding='UTF-8') as groups_created_file:
        reader = csv.DictReader(groups_created_file)
        for row in reader:
            if row['Group Name'] == group_name:
                return eval(row['Group ID'])
    return None


def sync_group_members_from_csv(signal_dbus, member_csv_file_path, groups_created_file_path):
    """
    Synchronize Signal group members from a CSV file.

    Args:
        signal_dbus (SignalDBus): An instance of the SignalDBus class.
        member_csv_file_path (str): Path to the CSV file containing member information.
        groups_created_file_path (str): Path to the CSV file containing created group information.
    """
    with open(member_csv_file_path, 'r', encoding='UTF-8') as member_csv_file:
        reader = csv.DictReader(member_csv_file)
        group_members = {}
        for row in reader:
            phone_number = row['Phone Number']
            group_name = row['Group Name']
            group_id = get_group_id_by_name(groups_created_file_path, group_name)
            if group_id:
                if group_id not in group_members:
                    group_members[group_id] = []
                group_members[group_id].append(phone_number)

    for group_id, members in group_members.items():
        group_name = signal_dbus.get_group_name(group_id)
        if group_name:
            print(f"Syncing members for group: {group_name}")
            existing_members = signal_dbus.get_group_property(group_id, 'Members')
            members_to_add = [member for member in members if member not in existing_members]
            members_to_remove = [member for member in existing_members if member not in members]
            if members_to_add:
                signal_dbus.add_members(group_id, members_to_add)
            if members_to_remove:
                signal_dbus.remove_members(group_id, members_to_remove)
        else:
            print(f"Group not found: {group_id}")


def main():
    """
    The main function to run the group synchronization.
    """
    registered_number = REGISTERED_NUMBER
    group_csv_file_path = 'env/groups.csv'
    groups_created_file_path = 'env/groups_created.csv'
    member_csv_file_path = 'env/members.csv'

    signal_dbus = SignalDBus(registered_number)
    create_groups_from_csv(signal_dbus, group_csv_file_path, groups_created_file_path)
    sync_group_members_from_csv(signal_dbus, member_csv_file_path, groups_created_file_path)


if __name__ == '__main__':
    main()