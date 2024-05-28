import csv
from pydbus import SystemBus  # type: ignore

class SignalDBus:
    def __init__(self, registered_number):
        self.registered_number = registered_number
        self.bus = SystemBus()
        self.signal_object = self.bus.get('org.asamk.Signal', object_path=f'/org/asamk/Signal/{registered_number.replace("+", "_")}')

    def is_registered(self, number):
        try:
            return self.signal_object.isRegistered(number)
        except Exception as e:
            if 'InvalidNumber' in str(e):
                return False
            raise e

    def is_registered_batch(self, numbers):
        results = []
        for number in numbers:
            try:
                result = self.signal_object.isRegistered(number)
                results.append(result)
            except Exception as e:
                if 'InvalidNumber' in str(e):
                    results.append(False)
                else:
                    raise e
        return results

    def create_group(self, group_name, members):
        registered_members = []
        unregistered_members = []

        if members:
            results = self.is_registered_batch(members)
            for member, is_registered in zip(members, results):
                if is_registered:
                    registered_members.append(member)
                else:
                    unregistered_members.append(member)

            if registered_members:
                try:
                    group_id = self.signal_object.createGroup(group_name, registered_members, "")
                    print(f"Created group '{group_name}' with {len(registered_members)} members")
                    return group_id
                except Exception as e:
                    print(f"Error creating group '{group_name}': {str(e)}")

            if unregistered_members:
                print(f"The following phone numbers are not registered with Signal: {', '.join(unregistered_members)}")
                with open('unregistered_numbers.txt', 'w') as file:
                    file.write('\n'.join(unregistered_members))
                print("Unregistered numbers saved to 'unregistered_numbers.txt'")
        else:
            try:
                group_id = self.signal_object.createGroup(group_name, [], "")
                print(f"Created group '{group_name}'")
                return group_id
            except Exception as e:
                print(f"Error creating group '{group_name}': {str(e)}")

    def update_group(self, group_id, members, remove_members=False):
        object_path = self.get_group_object_path(group_id)
        registered_members = []
        unregistered_members = []

        results = self.is_registered_batch(members)
        for member, is_registered in zip(members, results):
            if is_registered:
                registered_members.append(member)
            else:
                unregistered_members.append(member)

        if remove_members:
            if registered_members:
                try:
                    self.bus.get('org.asamk.Signal', object_path).removeMembers(registered_members)
                    print(f"Removed {len(registered_members)} members from the group")
                except Exception as e:
                    print(f"Error removing members from the group: {str(e)}")
        else:
            if registered_members:
                try:
                    self.bus.get('org.asamk.Signal', object_path).addMembers(registered_members)
                    print(f"Added {len(registered_members)} members to the group")
                except Exception as e:
                    print(f"Error adding members to the group: {str(e)}")

        if unregistered_members:
            print(f"The following phone numbers are not registered with Signal: {', '.join(unregistered_members)}")
            with open('unregistered_numbers.txt', 'a') as file:
                file.write('\n'.join(unregistered_members) + '\n')
            print("Unregistered numbers appended to 'unregistered_numbers.txt'")

    def list_groups(self):
        try:
            groups = self.signal_object.listGroups()
            return [(group[1], group[2]) for group in groups]
        except Exception as e:
            print(f"Error listing groups: {str(e)}")
            return []
        
    def remove_group(self, group_id):
        object_path = self.get_group_object_path(group_id)
        try:
            # Get the list of members in the group
            members = self.get_group_property(group_id, 'Members')

            # Remove all members from the group
            self.bus.get('org.asamk.Signal', object_path).removeMembers(members)

            # Quit the group
            self.bus.get('org.asamk.Signal', object_path).quitGroup()

            print(f"Removed all members and quit the group: {group_id}")
        except Exception as e:
            print(f"Error removing group: {str(e)}")

    def get_group_id(self, group_name):
        groups = self.list_groups()
        for group_id, name in groups:
            if name == group_name:
                return group_id
        return None

    def get_group_object_path(self, group_id):
        return self.signal_object.getGroup(group_id)

    def get_group_property(self, group_id, property_name):
        object_path = self.get_group_object_path(group_id)
        try:
            group_proxy = self.bus.get('org.asamk.Signal', object_path)
            return getattr(group_proxy, property_name)
        except Exception as e:
            print(f"Error getting group property '{property_name}': {str(e)}")
            return None

    def set_group_property(self, group_id, property_name, property_value):
        object_path = self.get_group_object_path(group_id)
        try:
            group_proxy = self.bus.get('org.asamk.Signal', object_path)
            setattr(group_proxy, property_name, property_value)
        except Exception as e:
            print(f"Error setting group property '{property_name}': {str(e)}")

    def get_all_group_properties(self, group_id):
        object_path = self.get_group_object_path(group_id)
        try:
            return self.bus.get('org.asamk.Signal', object_path).GetAll('org.asamk.Signal.Group')
        except Exception as e:
            print(f"Error getting all group properties: {str(e)}")
            return None

    def add_admins(self, group_id, recipients):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).addAdmins(recipients)
        except Exception as e:
            print(f"Error adding admins: {str(e)}")

    def add_members(self, group_id, recipients):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).addMembers(recipients)
        except Exception as e:
            print(f"Error adding members: {str(e)}")

    def disable_link(self, group_id):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).disableLink()
        except Exception as e:
            print(f"Error disabling link: {str(e)}")

    def enable_link(self, group_id, requires_approval):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).enableLink(requires_approval)
        except Exception as e:
            print(f"Error enabling link: {str(e)}")

    def quit_group(self, group_id):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).quitGroup()
        except Exception as e:
            print(f"Error quitting group: {str(e)}")

    def remove_admins(self, group_id, recipients):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).removeAdmins(recipients)
        except Exception as e:
            print(f"Error removing admins: {str(e)}")

    def remove_members(self, group_id, recipients):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).removeMembers(recipients)
        except Exception as e:
            print(f"Error removing members: {str(e)}")

    def reset_link(self, group_id):
        object_path = self.get_group_object_path(group_id)
        try:
            self.bus.get('org.asamk.Signal', object_path).resetLink()
        except Exception as e:
            print(f"Error resetting link: {str(e)}")

    @staticmethod
    def process_csv_file(file_path):
        members = []
        with open(file_path, 'r', encoding='UTF-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                phone_number = row['Phone Number']
                members.append(phone_number)
        return members