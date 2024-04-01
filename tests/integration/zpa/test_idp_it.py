import pytest
from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response

@pytest.fixture
def fs():
    yield

class TestIdP:
    """
    Integration Tests for the identity provider
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_idp(self, fs): 
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        try:
            # List all identity providers
            idps = client.idp.list_idps()
            assert isinstance(idps, list), "Expected a list of identity providers"
            if idps:  # If there are any identity providers
                # Select the first identity provider for further testing
                first_idp = idps[0]
                idp_id = first_idp.get('id')
                
                # Fetch the selected identity provider by its ID
                fetched_idp = client.idp.get_idp(idp_id)
                assert fetched_idp is not None, "Expected a valid identity provider object"
                assert fetched_idp.get('id') == idp_id, "Mismatch in identity provider ID"

                # Attempt to retrieve the identity provider by name
                idp_name = first_idp.get('name')
                idp_by_name= client.idp.get_idp_by_name(idp_name)
                assert idp_by_name is not None, "Expected a valid identity provider object when searching by name"
                assert idp_by_name.get('id') == idp_id, "Mismatch in identity provider ID when searching by name"
        except Exception as exc:
            errors.append(exc)

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during identity provider operations test: {errors}"
