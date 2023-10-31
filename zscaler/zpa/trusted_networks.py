from . import ZPAClient
from zscaler.utils import (
    delete_none_values,
)

class TrustedNetworksService:
    def __init__(self, client: ZPAClient):
        self.rest = client
        self.customer_id = client.customer_id

    def getByIDOrName(self, id=None, name=None):
        if id:
            network = self.getByID(id)
            if network:
                return network
        if name:
            return self.getByName(name)
        return None

    def getByID(self, id):
        endpoint = f"/mgmtconfig/v1/admin/customers/{self.customer_id}/network/{id}"
        response = self.rest.get(endpoint)

        if response.status_code != 200:
            return None
        return self._map_response_to_object(response.json())

    def getAll(self):
        endpoint = f"/mgmtconfig/v2/admin/customers/{self.customer_id}/network"
        networks_data = self.rest.get_paginated_data(base_url=endpoint, data_key_name="list")
        return [self._map_response_to_object(network) for network in networks_data]

    def getByName(self, name):
        networks = self.getAll()
        return next((network for network in networks if network["name"] == name), None)

    @staticmethod
    def _map_response_to_object(resp_json):
        if not isinstance(resp_json, dict):
            raise TypeError(f"Expected dict but received {type(resp_json)}")

        # Apply the delete_none_values directly to the dictionary
        return delete_none_values({
            "creation_time": resp_json.get("creationTime"),
            "id": resp_json.get("id"),
            "modified_by": resp_json.get("modifiedBy"),
            "modified_time": resp_json.get("modifiedTime"),
            "name": resp_json.get("name"),
            "network_id": resp_json.get("networkId"),
            "zscaler_cloud": resp_json.get("zscalerCloud"),
        })

    def map_object_to_request(self, network):
        if not network:
            return {}

        return {
            "creationTime": network.get("creation_time"),
            "id": network.get("id"),
            "modifiedBy": network.get("modified_by"),
            "modifiedTime": network.get("modified_time"),
            "name": network.get("name"),
            "networkId": network.get("network_id"),
            "zscalerCloud": network.get("zscaler_cloud"),
        }