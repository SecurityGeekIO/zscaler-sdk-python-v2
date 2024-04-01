import pytest

from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response

@pytest.fixture
def fs():
    yield

class TestServiceEdgeGroup:
    """
    Integration Tests for the Service Edge Group
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_service_edge_group(self, fs): 
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        group_name = "tests-service-edge-group"
        group_description = "tests-service-edge-group description"
        group_enabled = True
        latitude = "37.3382082"
        longitude = "-121.8863286"
        location = "San Jose, CA, USA"
        upgrade_day = "SUNDAY"
        upgrade_time_in_secs = "66600"
        override_version_profile = True
        version_profile_name = "Default"
        version_profile_id = "0"
        is_public = "TRUE"

        
        try:
            # Create a new service edge group
            created_group = client.service_edges.add_service_edge_group(
                name=group_name,
                description=group_description,
                enabled=group_enabled,
                latitude=latitude,
                longitude=longitude,
                location=location,
                upgrade_day=upgrade_day,
                upgrade_time_in_secs=upgrade_time_in_secs,
                override_version_profile=override_version_profile,
                version_profile_id=version_profile_id,
                version_profile_name=version_profile_name,
                is_public=is_public
            )
            assert created_group is not None
            assert created_group.name == group_name
            assert created_group.description == group_description
            assert created_group.enabled == group_enabled
            
            group_id = created_group.id
        except Exception as exc:
            errors.append(exc)

        try:
            # Retrieve the created service edge group by ID
            retrieved_group = client.service_edges.get_service_edge_group(group_id)
            assert retrieved_group.id == group_id
            assert retrieved_group.name == group_name
        except Exception as exc:
            errors.append(exc)

        try:
            # Update the service edge group
            updated_name = group_name + " Updated"
            client.service_edges.update_service_edge_group(group_id, name=updated_name)
            
            updated_group = client.service_edges.get_service_edge_group(group_id)
            assert updated_group.name == updated_name
        except Exception as exc:
            errors.append(exc)

        try:
            # List service edge groups and ensure the updated group is in the list
            groups_list = client.service_edges.list_service_edge_groups()
            assert any(group.id == group_id for group in groups_list)
        except Exception as exc:
            errors.append(exc)

        try:
            # Search for the service edge group by name
            search_result = client.service_edges.get_service_edge_group_by_name(updated_name)
            assert search_result is not None
            assert search_result.id == group_id
        except Exception as exc:
            errors.append(exc)

        try:
            # Delete the service edge group
            delete_response_code = client.service_edges.delete_service_edge_group(group_id)
            assert str(delete_response_code) == "204"
        except Exception as exc:
            errors.append(exc)

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during the service edge group lifecycle test: {errors}"
