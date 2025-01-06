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
from tests.test_utils import generate_random_string


@pytest.fixture
def fs():
    yield


class TestAccessPolicyIsolationRuleV2:
    """
    Integration Tests for the Access Policy Isolation Rules V2
    """

    def test_access_policy_isolation_rules_v2(self, fs):
        client = MockZPAClient(fs)
        errors = []  # Initialize an empty list to collect errors

        rule_id = None
        scim_group_ids = []
        profile_id = None

        try:
            # Test listing SCIM groups with pagination
            idps, _, err = client.zpa.idp.list_idps()
            if err or not isinstance(idps, list):
                raise AssertionError(f"Failed to retrieve IdPs: {err or f'Expected idps to be a list, got {type(idps)}'}")

            # Convert IDPs to dictionaries
            idps = [idp.as_dict() for idp in idps]

            # Find the IdP with ssoType = USER
            user_idp = next((idp for idp in idps if "USER" in idp.get("sso_type", [])), None)
            if not user_idp:
                raise AssertionError("No IdP with ssoType 'USER' found.")

            # Export the ID of the matching IdP
            user_idp_id = user_idp.get("id")
            if not user_idp_id:
                raise AssertionError("The matching IdP does not have an 'id' field.")

            # List SCIM groups using the exported IdP ID
            scim_groups, _, err = client.zpa.scim_groups.list_scim_groups(idp_id=user_idp_id)
            if err or not scim_groups:
                raise AssertionError(f"Failed to list SCIM groups: {err}")

            # Convert SCIMGroup objects to dictionaries
            scim_groups = [group.as_dict() for group in scim_groups]

            # Retrieve the IDs for the first two SCIM groups
            scim_group_ids = [(user_idp_id, group["id"]) for group in scim_groups[:2]]
            if len(scim_group_ids) < 2:
                raise AssertionError("Less than 2 SCIM groups were retrieved.")

            print(f"Exported IdP ID: {user_idp_id}")
            print(f"Retrieved SCIM Group IDs: {scim_group_ids}")

        except Exception as exc:
            errors.append(f"Listing SCIM groups failed: {exc}")

        try:
            # Test listing Isolation profiles
            profiles = client.zpa.cbi_zpa_profile.list_isolation_profiles()
            assert isinstance(profiles, list), "Response is not in the expected list format."
            assert len(profiles) > 0, "No Isolation profiles were found."
            profile_id = profiles[0]["id"]

        except Exception as exc:
            errors.append(f"Listing Isolation profiles failed: {exc}")

        try:
            # Create an Isolation Policy Rule
            rule_name = "tests-" + generate_random_string()
            rule_description = "updated-" + generate_random_string()
            created_rule = client.zpa.policies.add_isolation_rule_v2(
                name=rule_name,
                description=rule_description,
                action="isolate",
                zpn_isolation_profile_id=profile_id,
                conditions=[
                    ("scim_group", scim_group_ids),
                ],
            )
            assert created_rule is not None, "Failed to create Isolation Policy Rule"
            rule_id = created_rule.get("id", None)
        except Exception as exc:
            errors.append(f"Failed to create Isolation Policy Rule: {exc}")

        try:
            # Test listing Isolation Policy Rules
            all_forwarding_rules = client.zpa.policies.list_rules("isolation")
            assert any(rule["id"] == rule_id for rule in all_forwarding_rules), "Isolation Policy Rules not found in list"
        except Exception as exc:
            errors.append(f"Failed to list Isolation Policy Rules: {exc}")

        try:
            # Test retrieving the specific Isolation Policy Rule
            retrieved_rule = client.zpa.policies.get_rule("isolation", rule_id)
            assert retrieved_rule["id"] == rule_id, "Failed to retrieve the correct Isolation Policy Rule"
        except Exception as exc:
            errors.append(f"Failed to retrieve Isolation Policy Rule: {exc}")

        try:
            # Update the Isolation Policy Rule
            updated_rule_description = "Updated " + generate_random_string()
            updated_rule = client.zpa.policies.update_isolation_rule_v2(
                rule_id=rule_id,
                description=updated_rule_description,
                action="isolate",
                zpn_isolation_profile_id=profile_id,
                conditions=[
                    ("scim_group", scim_group_ids),
                ],
            )
            assert (
                updated_rule["description"] == updated_rule_description
            ), "Failed to update description for Isolation Policy Rule"
        except Exception as exc:
            errors.append(f"Failed to update Isolation Policy Rule: {exc}")

        finally:
            # Ensure cleanup is performed even if there are errors
            if rule_id:
                try:
                    delete_status_rule = client.zpa.policies.delete_rule("isolation", rule_id)
                    assert delete_status_rule == 204, "Failed to delete Isolation Policy Rule"
                except Exception as cleanup_exc:
                    errors.append(f"Cleanup failed: {cleanup_exc}")

        # Assert that no errors occurred during the test
        assert len(errors) == 0, f"Errors occurred during the Isolation Policy Rule operations test: {errors}"
