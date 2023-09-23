from .zia_client import ZIAClientHelper
import delete_none

class ZiaFWTimeWindowsService:
    def __init__(self, module):
        self.module = module
        self.rest = ZIAClientHelper(module)

    def getByIDOrName(self, id, name):
        fwTime = None
        if id is not None:
            fwTime = self.getByID(id)
        if fwTime is None and name is not None:
            fwTime = self.getByName(name)
        return fwTime

    def getByID(self, id):
        response = self.rest.get("/timeWindows" % (id))
        status_code = response.status_code
        if status_code != 200:
            return None
        return self.mapRespJSONToApp(response.json)

    def getAll(self):
        list = self.rest.get_paginated_data(
            base_url="/timeWindows" % (self.customer_id), data_key_name="list"
        )
        fwTimes = []
        for fwTime in list:
            fwTimes.append(self.mapRespJSONToApp(fwTime))
        return fwTimes

    def getByName(self, name):
        fwTimes = self.getAll()
        for role in fwTimes:
            if role.get("name") == name:
                return role
        return None

    @delete_none
    def mapRespJSONToApp(self, resp_json):
        if resp_json is None:
            return {}
        return {
            "id": resp_json.get("id"),
            "name": resp_json.get("name"),
            "start_time": resp_json.get("startTime"),
            "end_time": resp_json.get("endTime"),
            "day_of_week": resp_json.get("dayOfWeek"),
        }

    @delete_none
    def mapAppToJSON(self, fwTime):
        if fwTime is None:
            return {}
        return {
            "id": fwTime.get("id"),
            "name": fwTime.get("name"),
            "startTime": fwTime.get("start_time"),
            "endTime": fwTime.get("end_time"),
            "dayOfWeek": fwTime.get("day_of_week"),
        }
