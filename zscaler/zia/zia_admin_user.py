from .zia_client import ZIAClientHelper
import delete_none

class ZiaAdminUserService:
    def __init__(self, module):
        self.module = module
        self.rest = ZIAClientHelper(module)

    def getByIDOrName(self, id, name):
        user = None
        if id is not None:
            user = self.getByID(id)
        if user is None and name is not None:
            user = self.getByName(name)
        return user

    def getByID(self, id):
        response = self.rest.get("/adminUsers/%s" % (self.module, id))
        status_code = response.status_code
        if status_code != 200:
            return None
        return self.mapRespJSONToApp(response.json)

    def getAll(self):
        list = self.rest.get_paginated_data(
            base_url="/adminUsers/" % (self), data_key_name="list"
        )
        users = []
        for user in list:
            users.append(self.mapRespJSONToApp(user))
        return users

    def getByLoginName(self, login_name):
        login_names = self.getAll()
        for login_name in login_names:
            if login_name.get("login_name") == login_name:
                return login_name
        return None

    def getByUserName(self, username):
        usernames = self.getAll()
        for username in usernames:
            if username.get("username") == username:
                return username
        return None

    def getByEmail(self, email):
        emails = self.getAll()
        for email in emails:
            if email.get("email") == email:
                return email
        return None

    @delete_none
    def mapRespJSONToApp(self, resp_json):
        if resp_json is None:
            return {}
        return {
            "id": resp_json.get("id"),
            "login_name": resp_json.get("loginName"),
            "username": resp_json.get("userName"),
            "email": resp_json.get("email"),
            "comments": resp_json.get("comments"),
            "is_non_editable": resp_json.get("isNonEditable"),
            "disabled": resp_json.get("disabled"),
            "is_auditor": resp_json.get("isAuditor"),
            "password": resp_json.get("password"),
            "is_password_login_allowed": resp_json.get("isPasswordLoginAllowed"),
            "is_security_report_comm_enabled": resp_json.get(
                "isSecurityReportCommEnabled"
            ),
            "is_service_update_comm_enabled": resp_json.get(
                "isServiceUpdateCommEnabled"
            ),
            "is_product_update_comm_enabled": resp_json.get(
                "isProductUpdateCommEnabled"
            ),
            "is_password_expired": resp_json.get("isPasswordExpired"),
            "is_exec_mobile_app_enabled": resp_json.get("isExecMobileAppEnabled"),
        }

    @delete_none
    def mapAppToJSON(self, user):
        if user is None:
            return {}
        return {
            "id": user.get("id"),
            "loginName": user.get("loginName"),
            "userName": user.get("description"),
            "email": user.get("email"),
            # "role": user.get("role"), - Need to expand this menu
            "comments": user.get("comments"),
            "isNonEditable": user.get("isNonEditable"),
            "disabled": user.get("disabled"),
            "isAuditor": user.get("isAuditor"),
            "password": user.get("password"),
            "isPasswordLoginAllowed": user.get("is_password_login_allowed"),
            "isSecurityReportCommEnabled": user.get("is_security_report_comm_enabled"),
            "isServiceUpdateCommEnabled": user.get("is_service_update_comm_enabled"),
            "isProductUpdateCommEnabled": user.get("is_product_update_comm_enabled"),
            "isPasswordExpired": user.get("is_password_expired"),
            "isExecMobileAppEnabled": user.get("is_exec_mobile_app_enabled"),
        }

    def create(self, user):
        """Create new Admin User"""
        userJSON = self.mapAppToJSON(user)
        response = self.rest.post("/adminUsers" % (self), data=userJSON)
        status_code = response.status_code
        if status_code > 299:
            return None
        return self.mapRespJSONToApp(response.json)

    def update(self, user):
        """update the Admin User Account"""
        userJSON = self.mapAppToJSON(user)
        response = self.rest.put(
            "/adminUsers/%s" % (self, userJSON.get("id")), data=userJSON
        )
        status_code = response.status_code
        if status_code > 299:
            return None
        return user

    def delete(self, id):
        """delete the Admin User Account"""
        response = self.rest.delete("/adminUsers/%s" % (self, id))
        return response.status_code
