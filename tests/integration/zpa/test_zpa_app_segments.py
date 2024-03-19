# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import pytest

from tests.integration.zpa.mocks import MockZPAClient
from tests.integration.zpa.mocks import modify_request, modify_response


@pytest.fixture
def fs():
    yield


class TestApplicationSegment:
    """
    Integration Tests for the Applications Segment
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_application_segment_crud(self, fs):
        # Instantiate Mock Client
        client = MockZPAClient(fs)
        errors = []
        group = None
        try:
            group = client.segment_groups.add_group(
                name="itest app group",
            )
        except Exception as exc:
            errors.append(exc)
        app = None
        try:
            app = client.app_segments.add_segment(
                name="itest-appsegment",
                domain_names=["crm.example.com"],
                segment_group_id=group.id,
                server_group_ids=[],
                tcp_port_ranges=["80", "80"],
            )
            assert len(app) > 0
            assert app.name == "itest-appsegment"
            assert app.tcp_port_ranges == ["80", "80"]
        except Exception as exc:
            errors.append(exc)

        try:
            remote_app = client.app_segments.get_segment(segment_id=app.id)
            assert remote_app.name == app.name
            assert remote_app.tcp_port_ranges == ["80", "80"]
        except Exception as exc:
            errors.append(exc)

        try:
            remote_app = client.app_segments.get_segment_by_name(name=app.name)
            assert remote_app.id == app.id
            assert remote_app.tcp_port_ranges == ["80", "80"]
        except Exception as exc:
            errors.append(exc)

        try:
            apps = client.app_segments.list_segments()
            assert len(apps) > 0
        except Exception as exc:
            errors.append(exc)

        try:
            status = client.app_segments.delete_segment(segment_id=app.id, force_delete=True)
            assert status > 200 and status < 299
        except Exception as exc:
            errors.append(exc)

        try:
            status = client.segment_groups.delete_group(group_id=group.id)
            assert status > 200 and status < 299
        except Exception as exc:
            errors.append(exc)

        assert len(errors) == 0
