import csv
import os

from dotenv import load_dotenv
from signal_dbus import SignalDBus

load_dotenv()
REGISTERED_NUMBER = os.getenv("REGISTERED_NUMBER")


def create_groups_from_csv(signal_dbus, group_csv_file_path):
    # Read the group CSV file and create groups
    with open(group_csv_file_path, 'r', encoding='UTF-8') as group_csv_file:
        reader = csv.DictReader(group_csv_file)
        rows = list(reader)

    updated_rows = []
    for row in rows:
        group_id = eval(row['Group ID']) if row['Group ID'] else None
        group_name = row['Group Name']
        group_description = row['Group Description']
        permission_add_members = row['PermissionAddMembers']
        permission_edit_details = row['PermissionEditDetails']
        permission_send_messages = row['PermissionSendMessages']
        
        # Create the group if it doesn't exist and update the group ID in the CSV
        if not group_id:
            group_id = signal_dbus.create_group(group_name, [])
            print(group_id)
            row['Group ID'] = str(group_id)
            signal_dbus.set_group_property(group_id, 'Description', group_description)
            signal_dbus.set_group_property(group_id, 'PermissionAddMembers', permission_add_members)
            signal_dbus.set_group_property(group_id, 'PermissionEditDetails', permission_edit_details)
            signal_dbus.set_group_property(group_id, 'PermissionSendMessages', permission_send_messages)
            print(f"Created group: {group_name}")
        else:
            print(f"Group already exists: {group_name}")
        
        updated_rows.append(row)

    # Write the updated group IDs back to the CSV file
    with open(group_csv_file_path, 'w', encoding='UTF-8', newline='') as group_csv_file:
        fieldnames = ['Group ID', 'Group Name', 'Group Description', 'PermissionAddMembers', 'PermissionEditDetails', 'PermissionSendMessages']
        writer = csv.DictWriter(group_csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

def sync_group_members_from_csv(signal_dbus, member_csv_file_path):
    # Read the member CSV file and process the data
    with open(member_csv_file_path, 'r', encoding='UTF-8') as member_csv_file:
        reader = csv.DictReader(member_csv_file)
        group_members = {}
        for row in reader:
            phone_number = row['Phone Number']
            group_id = eval(row['Group ID'])
            if group_id not in group_members:
                group_members[group_id] = []
            group_members[group_id].append(phone_number)

    # Iterate over each group and sync members
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
    registered_number = REGISTERED_NUMBER  # Replace with the registered Signal number
    group_csv_file_path = 'env/groups.csv'  # Replace with the path to your group CSV file
    member_csv_file_path = 'env/members.csv'  # Replace with the path to your member CSV file

    signal_dbus = SignalDBus(registered_number)
    create_groups_from_csv(signal_dbus, group_csv_file_path)
    #sync_group_members_from_csv(signal_dbus, member_csv_file_path)

if __name__ == '__main__':
    main()