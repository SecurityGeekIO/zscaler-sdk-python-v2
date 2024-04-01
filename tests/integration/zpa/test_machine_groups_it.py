import pytest
from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response

@pytest.fixture
def fs():
    yield

class TestMachineGroups:
    """
    Integration Tests for the Machine Groups
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_machine_groups(self, fs): 
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        try:
            # List all machine groups
            machine_groups = client.machine_groups.list_groups()
            assert isinstance(machine_groups, list), "Expected a list of machine groups"
            if machine_groups:  # If there are any machine groups
                # Select the first machine group for further testing
                first_group = machine_groups[0]
                group_id = first_group.get('id')
                
                # Fetch the selected machine group by its ID
                fetched_group = client.machine_groups.get_group(group_id)
                assert fetched_group is not None, "Expected a valid machine group object"
                assert fetched_group.get('id') == group_id, "Mismatch in machine group ID"

                # Attempt to retrieve the machine group by name
                group_name = first_group.get('name')
                group_by_name = client.machine_groups.get_machine_group_by_name(group_name)
                assert group_by_name is not None, "Expected a valid machine group object when searching by name"
                assert group_by_name.get('id') == group_id, "Mismatch in machine group ID when searching by name"
        except Exception as exc:
            errors.append(exc)

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during machine groups test: {errors}"
