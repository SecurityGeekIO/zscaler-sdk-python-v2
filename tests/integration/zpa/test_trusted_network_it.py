import pytest
from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response

@pytest.fixture
def fs():
    yield

class TestTrustedNetworks:
    """
    Integration Tests for the Trusted Networks
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_trusted_networks(self, fs): 
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        try:
            # List all trusted networks
            trusted_networks = client.trusted_networks.list_networks()
            assert isinstance(trusted_networks, list), "Expected a list of trusted networks"
            if trusted_networks:  # If there are any trusted networks
                # Select the first trusted network for further testing
                first_network = trusted_networks[0]
                network_id = first_network.get('id')
                
                # Fetch the selected trusted network by its ID
                fetched_network = client.trusted_networks.get_network(network_id)
                assert fetched_network is not None, "Expected a valid trusted network object"
                assert fetched_network.get('id') == network_id, "Mismatch in trusted network ID"

                # Attempt to retrieve the trusted network by name
                network_name = first_network.get('name')
                network_by_name= client.trusted_networks.get_network_by_name(network_name)
                assert network_by_name is not None, "Expected a valid trusted network object when searching by name"
                assert network_by_name.get('id') == network_id, "Mismatch in trusted network ID when searching by name"
        except Exception as exc:
            errors.append(exc)

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during trusted network operations test: {errors}"
