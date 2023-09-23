from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule
from pyzscaler import ZIA


class ZiaFWFilteringRuleService:
    def __init__(self, module: AnsibleModule, client: ZIA) -> None:
        self.module = module
        self.client = client

    def getByID(self, group_id):
        if group_id is None:
            return None
        try:
            group = self.client.firewall.get_rule(group_id)
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
        return self.client.firewall.list_rules().to_list()

    # Need to review the schema
    def create(self, rule):
        return self.client.firewall.add_rule(
            name=rule.get("name", ""),
            order=rule.get("order", ""),
            rank=rule.get("rank", ""),
            locations=rule.get("locations", ""),
            location_groups=rule.get("location_groups", ""),
            departments=rule.get("departments", ""),
            groups=rule.get("groups", ""),
            users=rule.get("users", ""),
            time_windows=rule.get("time_windows", ""),
            last_modified_by=rule.get("last_modified_by", ""),
            src_ips=rule.get("src_ips", ""),
            src_ip_groups=rule.get("src_ip_groups", ""),
            dest_addresses=rule.get("dest_addresses", ""),
            dest_ip_categories=rule.get("dest_ip_categories", ""),
            dest_countries=rule.get("dest_countries", ""),
            dest_ip_groups=rule.get("dest_ip_groups", ""),
            nw_services=rule.get("nw_services", ""),
            nw_service_groups=rule.get("nw_service_groups", ""),
            nw_applications=rule.get("nw_applications", ""),
            nw_application_groups=rule.get("nw_application_groups", ""),
            app_services=rule.get("app_services", ""),
            app_service_groups=rule.get("app_service_groups", ""),
            labels=rule.get("labels", ""),
            action=rule.get("action", ""),
            state=rule.get("state", ""),
            last_modified_time=rule.get("last_modified_time", ""),
            default_rule=rule.get("default_rule", ""),
            predefined=rule.get("predefined", ""),
        ).to_dict()

    # Need to add the schema
    def update(self, rule):
        return self.client.firewall.update_rule(
            rule_id=rule.get("id", ""),
            name=rule.get("name", ""),
            order=rule.get("order", ""),
            rank=rule.get("rank", ""),
            locations=rule.get("locations", ""),
            location_groups=rule.get("location_groups", ""),
            departments=rule.get("departments", ""),
            groups=rule.get("groups", ""),
            users=rule.get("users", ""),
            time_windows=rule.get("time_windows", ""),
            last_modified_by=rule.get("last_modified_by", ""),
            src_ips=rule.get("src_ips", ""),
            src_ip_groups=rule.get("src_ip_groups", ""),
            dest_addresses=rule.get("dest_addresses", ""),
            dest_ip_categories=rule.get("dest_ip_categories", ""),
            dest_countries=rule.get("dest_countries", ""),
            dest_ip_groups=rule.get("dest_ip_groups", ""),
            nw_services=rule.get("nw_services", ""),
            nw_service_groups=rule.get("nw_service_groups", ""),
            nw_applications=rule.get("nw_applications", ""),
            nw_application_groups=rule.get("nw_application_groups", ""),
            app_services=rule.get("app_services", ""),
            app_service_groups=rule.get("app_service_groups", ""),
            labels=rule.get("labels", ""),
            action=rule.get("action", ""),
            state=rule.get("state", ""),
            last_modified_time=rule.get("last_modified_time", ""),
            default_rule=rule.get("default_rule", ""),
            predefined=rule.get("predefined", ""),
        ).to_dict()

    def delete(self, group_id):
        code = self.client.firewall.delete_rule(group_id)
        if code != 200:
            return None
        return group_id
