import pytest
from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response

@pytest.fixture
def fs():
    yield

class TestPostureProfile:
    """
    Integration Tests for the Posture Profile
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_posture_profile(self, fs): 
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        try:
            # List all posture profiles
            posture_profiles = client.posture_profiles.list_profiles()
            assert isinstance(posture_profiles, list), "Expected a list of posture profiles"
            if posture_profiles:  # If there are any posture profiles
                # Select the first posture profile for further testing
                first_profile = posture_profiles[0]
                profile_id = first_profile.get('id')
                
                # Fetch the selected posture profile by its ID
                fetched_profile = client.posture_profiles.get_profile(profile_id)
                assert fetched_profile is not None, "Expected a valid posture profile object"
                assert fetched_profile.get('id') == profile_id, "Mismatch in posture profile ID"

                # Attempt to retrieve the posture profile by name
                profile_name = first_profile.get('name')
                profile_by_name= client.posture_profiles.get_profile_by_name(profile_name)
                assert profile_by_name is not None, "Expected a valid posture profile object when searching by name"
                assert profile_by_name.get('id') == profile_id, "Mismatch in posture profile ID when searching by name"
        except Exception as exc:
            errors.append(exc)

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during posture profile operations test: {errors}"
