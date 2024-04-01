import pytest

from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response


@pytest.fixture
def fs():
    yield


class TestSegmentGroup:
    """
    Integration Tests for the Segment Group
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_application_server(self, fs): 
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        server_name = "Test application server"
        server_description = "A test application server for integration tests."
        server_address = "192.168.200.1"
        
        try:
            # Create a new application server
            created_server = client.servers.add_server(name=server_name, description=server_description, enabled=True, address=server_address)
            assert created_server is not None
            assert created_server.name == server_name
            assert created_server.description == server_description
            assert created_server.address == server_address
            assert created_server.enabled is True
            
            server_id = created_server.id
        except Exception as exc:
            errors.append(exc)

        try:
            # Retrieve the created segment group by ID
            retrieved_server = client.servers.get_server(server_id)
            assert retrieved_server.id == server_id
            assert retrieved_server.name == server_name
        except Exception as exc:
            errors.append(exc)

        try:
            # Update the segment group
            updated_name = server_name + " Updated"
            client.servers.update_server(server_id, name=updated_name)
            
            updated_group = client.servers.get_server(server_id)
            assert updated_group.name == updated_name
        except Exception as exc:
            errors.append(exc)

        try:
            # List segment groups and ensure the updated group is in the list
            groups_list = client.servers.list_servers()
            assert any(group.id == server_id for group in groups_list)
        except Exception as exc:
            errors.append(exc)

        try:
            # Search for the segment group by name
            search_result = client.servers.get_server_by_name(updated_name)
            assert search_result is not None
            assert search_result.id == server_id
        except Exception as exc:
            errors.append(exc)

        try:
            # Delete the segment group
            delete_response_code = client.servers.delete_server(server_id)
            assert str(delete_response_code) == "204"
        except Exception as exc:
            errors.append(exc)

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during the application server lifecycle test: {errors}"
