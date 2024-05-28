import csv
import subprocess

class SignalCommands:
    def __init__(self, registered_number):
        self.registered_number = registered_number

    def create_group(self, group_name, members):
        try:
            command = [
                'signal-cli',
                '-u',
                self.registered_number,
                'updateGroup',
                '-n',
                group_name
            ]
            if members:
                command.extend(['-m'] + members)
            subprocess.run(command, check=True)
            print(f"Created group '{group_name}' with {len(members)} members")
        except subprocess.CalledProcessError as e:
            print(f"Error creating group '{group_name}': {str(e)}")

    def update_group(self, group_id, members, remove_members=False):
        if remove_members:
            try:
                command = [
                    'signal-cli',
                    '-u',
                    self.registered_number,
                    'updateGroup',
                    '-g',
                    group_id,
                    '-d'
                ]
                command.extend(members)
                subprocess.run(command, check=True)
                print(f"Removed {len(members)} members from the group")
            except subprocess.CalledProcessError as e:
                print(f"Error removing members from the group: {str(e)}")
        else:
            try:
                command = [
                    'signal-cli',
                    '-u',
                    self.registered_number,
                    'updateGroup',
                    '-g',
                    group_id
                ]
                command.extend(['-m'] + members)
                subprocess.run(command, check=True)
                print(f"Added {len(members)} members to the group")
            except subprocess.CalledProcessError as e:
                print(f"Error adding members to the group: {str(e)}")

    def list_groups(self):
        try:
            command = [
                'signal-cli',
                '-u',
                self.registered_number,
                'listGroups'
            ]
            output = subprocess.check_output(command, universal_newlines=True)
            groups = []
            for line in output.strip().split('\n'):
                if 'Active: true' in line:
                    group_id = line.split('Id: ')[1].split(' ')[0]
                    group_name = line.split('Name: ')[1].split(' ')[0]
                    groups.append((group_id, group_name))
            return groups
        except subprocess.CalledProcessError as e:
            print(f"Error listing groups: {str(e)}")
            return []

    @staticmethod
    def process_csv_file(file_path):
        members = []
        with open(file_path, 'r', encoding='UTF-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                phone_number = row['Phone Number']
                members.append(phone_number)
        return members