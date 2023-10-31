from . import ZPAClient
from requests import Response


class ApplicationSegmentService:
    def __init__(self, client: ZPAClient):
        self.rest = client
        self.customer_id = client.customer_id

    def getByIDOrName(self, id, name):
        app = None
        if id is not None:
            app = self.getByID(id)
        if app is None and name is not None:
            app = self.getByName(name)
        return app

    def getByID(self, id):
        response = self.rest.get("/mgmtconfig/v1/admin/customers/%s/application/%s" % (self.customer_id, id))
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code != 200:
                return None
        return response

    def getAll(self):
        list, error_message = self.rest.get_paginated_data(
            base_url="/mgmtconfig/v1/admin/customers/%s/application" % (self.customer_id),
            data_key_name="list",
        )
        apps = []
        for app in list:
            apps.append(app)
        return apps

    def getByName(self, name):
        apps = self.getAll()
        for app in apps:
            if app.get("name") == name:
                return app
        return None

    def create(self, app):
        """Create new application"""
        response = self.rest.post(
            "/mgmtconfig/v1/admin/customers/%s/application" % (self.customer_id),
            data=app,
        )
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                return None
        return self.getByID(response.get("id"))

    def update(self, app):
        """update the application"""
        response = self.rest.put(
            "/mgmtconfig/v1/admin/customers/%s/application/%s" % (self.customer_id, app.get("id")),
            data=app,
        )
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                return None
        return self.getByID(app.get("id"))

    def detach_from_segment_group(self, app_id, seg_group_id):
        seg_group = self.rest.get("/mgmtconfig/v1/admin/customers/%s/segmentGroup/%s" % (self.customer_id, seg_group_id))
        if isinstance(seg_group, Response):
            status_code = seg_group.status_code
            if status_code > 299:
                return None
        apps = seg_group.get("applications", [])
        addaptedApps = []
        for app in apps:
            if app.get("id") != app_id:
                addaptedApps.append(app)
        seg_group["applications"] = addaptedApps
        self.rest.put(
            "/mgmtconfig/v1/admin/customers/%s/segmentGroup/%s" % (self.customer_id, seg_group_id),
            data=seg_group,
        )

    def delete(self, id):
        """delete the application"""
        response = self.rest.delete("/mgmtconfig/v1/admin/customers/%s/application/%s" % (self.customer_id, id))
        return response.status_code