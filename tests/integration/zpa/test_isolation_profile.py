"""
Copyright (c) 2023, Zscaler Inc.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import pytest

from tests.integration.zpa.conftest import MockZPAClient


@pytest.fixture
def fs():
    yield


class TestIsolationProfile:
    """
    Integration Tests for the Isolation Profile.
    """

    def test_isolation_profile(self, fs):
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        # Attempt to list all isolation profiles
        try:
            isolation_profiles = client.isolation.list_profiles()
            assert isinstance(isolation_profiles, list), "Expected a list of isolation profiles"
        except Exception as exc:
            errors.append(f"Listing isolation profiles failed: {str(exc)}")

        # Process each isolation profile if the list is not empty
        if isolation_profiles:
            for first_profile in isolation_profiles:
                profile_id = first_profile.get("id")

                # Fetch the selected isolation profile by its ID
                try:
                    fetched_profile = client.isolation.get_profile_by_id(profile_id)
                    assert fetched_profile is not None, "Expected a valid isolation profile object"
                    assert fetched_profile.get("id") == profile_id, "Mismatch in isolation profile ID"
                except Exception as exc:
                    errors.append(f"Fetching isolation profile by ID failed: {str(exc)}")

                # Attempt to retrieve the isolation profile by name
                try:
                    profile_name = first_profile.get("name")
                    profile_by_name = client.isolation.get_profile_by_name(profile_name)
                    assert profile_by_name is not None, "Expected a valid isolation profile object when searching by name"
                    assert profile_by_name.get("id") == profile_id, "Mismatch in isolation profile ID when searching by name"
                except Exception as exc:
                    errors.append(f"Fetching isolation profile by name failed: {str(exc)}")

                # Once we've tested one profile, exit the loop to avoid redundant testing
                break

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during isolation profile operations test: {errors}"
