from .zia_client import ZIAClientHelper
import delete_none

class ZiaDLPDictionariesService:
    def __init__(self, module):
        self.module = module
        self.rest = ZIAClientHelper(module)

    def getByIDOrName(self, id, name):
        dlp = None
        if id is not None:
            dlp = self.getByID(id)
        if dlp is None and name is not None:
            dlp = self.getByName(name)
        return dlp

    def getByID(self, id):
        response = self.rest.get("/dlpDictionaries/%s" % (self.module, id))
        status_code = response.status_code
        if status_code != 200:
            return None
        return self.mapRespJSONToApp(response.json)

    def getAll(self):
        list = self.rest.get_paginated_data(
            base_url="/dlpDictionaries/" % (self), data_key_name="list"
        )
        users = []
        for user in list:
            users.append(self.mapRespJSONToApp(user))
        return users

    def getByName(self, name):
        users = self.getAll()
        for user in users:
            if user.get("name") == name:
                return user
        return None

    @delete_none
    def mapRespJSONToApp(self, resp_json):
        if resp_json is None:
            return {}
        return {
            "id": resp_json.get("id"),
            "name": resp_json.get("name"),
            "description": resp_json.get("description"),
            "confidence_threshold": resp_json.get("confidenceThreshold"),
            # "phrases": resp_json.get("phrases"), Need to expand this menu
            "custom_phrase_match_type": resp_json.get("customPhraseMatchType"),
            # "patterns": resp_json.get("patterns"), Need to expand this menu
            "name_l10n_tag": resp_json.get("nameL10nTag"),
            "threshold_type": resp_json.get("thresholdType"),
            "dictionary_type": resp_json.get("dictionaryType"),
            # "exact_data_match_details": resp_json.get("exactDataMatchDetails"), Need to expand this menu
            # "idm_profile_match_accuracy": resp_json.get("idmProfileMatchAccuracy"), Need to expand this menu
            "proximity": resp_json.get("proximity"),
            "custom": resp_json.get("custom"),
            "proximity_length_enabled": resp_json.get("proximityLengthEnabled"),
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

    def create(self, dlp):
        """Create new DLP Dictionaries"""
        dlpJSON = self.mapAppToJSON(dlp)
        response = self.rest.post("/dlpDictionaries" % (self), data=dlpJSON)
        status_code = response.status_code
        if status_code > 299:
            return None
        return self.mapRespJSONToApp(response.json)

    def update(self, dlp):
        """update the DLP Dictionaries"""
        dlpJSON = self.mapAppToJSON(dlp)
        response = self.rest.put(
            "/dlpDictionaries/%s" % (self, dlpJSON.get("id")), data=dlpJSON
        )
        status_code = response.status_code
        if status_code > 299:
            return None
        return dlp

    def delete(self, id):
        """delete the DLP Dictionaries"""
        response = self.rest.delete("/dlpDictionaries/%s" % (self, id))
        return response.status_code
