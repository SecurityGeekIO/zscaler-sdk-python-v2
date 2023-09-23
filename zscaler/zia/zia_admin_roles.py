from .zia_client import ZIAClientHelper
import delete_none

class ZiaAdminRoleService:
    def __init__(self, module, customer_id):
        self.module = module
        self.customer_id = customer_id
        self.rest = ZIAClientHelper(module)

    def getByIDOrName(self, id, name):
        role = None
        if id is not None:
            role = self.getByID(id)
        if role is None and name is not None:
            role = self.getByName(name)
        return role

    def getByID(self, id):
        response = self.rest.get("/adminRoles/lite" % (id))
        status_code = response.status_code
        if status_code != 200:
            return None
        return self.mapRespJSONToApp(response.json)

    def getAll(self):
        list = self.rest.get_paginated_data(
            base_url="/adminRoles/lite" % (self.customer_id), data_key_name="list"
        )
        roles = []
        for role in list:
            roles.append(self.mapRespJSONToApp(role))
        return roles

    def getByName(self, name):
        roles = self.getAll()
        for role in roles:
            if role.get("name") == name:
                return role
        return None

    @delete_none
    def mapRespJSONToApp(self, resp_json):
        if resp_json is None:
            return {}
        return {
            "id": resp_json.get("id"),
            "rank": resp_json.get("rank"),
            "name": resp_json.get("name"),
            "policy_access": resp_json.get("policyAccess"),
            "dashboard_access": resp_json.get("dashboardAccess"),
            "report_access": resp_json.get("reportAccess"),
            "analysis_access": resp_json.get("analysisAccess"),
            "username_access": resp_json.get("usernameAccess"),
            "admin_acct_access": resp_json.get("adminAcctAccess"),
            "is_auditor": resp_json.get("isAuditor"),
            "permissions": resp_json.get("permissions"),
            "is_non_editable": resp_json.get("isNonEditable"),
            "logs_limit": resp_json.get("logsLimit"),
            "role_type": resp_json.get("roleType"),
        }

    @delete_none
    def mapAppToJSON(self, network):
        if network is None:
            return {}
        return {
            "id": network.get("id"),
            "rank": network.get("rank"),
            "name": network.get("name"),
            "policyAccess": network.get("policy_access"),
            "dashboardAccess": network.get("dashboard_access"),
            "reportAccess": network.get("report_access"),
            "analysisAccess": network.get("analysis_access"),
            "usernameAccess": network.get("username_access"),
            "adminAcctAccess": network.get("admin_acct_access"),
            "isAuditor": network.get("is_auditor"),
            "permissions": network.get("permissions"),
            "isNonEditable": network.get("is_non_editable"),
            "logsLimit": network.get("logs_limit"),
            "roleType": network.get("role_type"),
        }
