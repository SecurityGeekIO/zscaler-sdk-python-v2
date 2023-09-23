from __future__ import absolute_import, division, print_function

__metaclass__ = type


from pyzscaler import ZIA
from ansible.module_utils.basic import AnsibleModule


class ZiaFWIPDestinationGroupService:
    def __init__(self, module: AnsibleModule, client: ZIA) -> None:
        self.module = module
        self.client = client

    def getByID(self, group_id):
        if group_id is None:
            return None
        try:
            group = self.client.firewall.get_ip_destination_group(group_id)
            return group.to_dict()
        except:
            return None


    def getByName(self, name):
        if name is None:
            return None
        names = self.getAll()
        for name in names:
            if name.get("name", None) == name:
                return name
        return None

    def getByIDOrName(self, id, name):
        group = self.getByID(id)
        if group is not None:
            return group
        return self.getByName(name)

    def getAll(self):
        return self.client.firewall.list_ip_destination_groups().to_list()

    def create(self, group):
        return self.client.firewall.add_ip_destination_group(
            name=group.get("name", ""),
            type=group.get("type", ""),
            addresses=group.get("addresses", ""),
            description=group.get("description", ""),
            ip_categories=group.get("ip_categories", ""),
            countries=group.get("countries", "")
        ).to_dict()

    def update(self, group):
        return self.client.firewall.update_ip_destination_group(
            group_id=group.get("id", ""),
            name=group.get("name", ""),
            type=group.get("type", ""),
            addresses=group.get("addresses", ""),
            description=group.get("description", ""),
            ip_categories=group.get("ip_categories", ""),
            countries=group.get("countries", "")
        ).to_dict()

    def delete(self, group_id):
        code = self.client.firewall.delete_ip_destination_group(group_id)
        if code != 200:
            return None
        return group_id
