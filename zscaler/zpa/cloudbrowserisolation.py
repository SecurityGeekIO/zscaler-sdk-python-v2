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

from zscaler.api_client import APIClient
from zscaler.zpa.models.cloudbrowserisolation import CBIProfile
from zscaler.zpa.models.cloudbrowserisolation import ZPACBIProfile
from zscaler.zpa.models.cloudbrowserisolation import CBIRegion
from zscaler.zpa.models.cloudbrowserisolation import CBICertificate
from zscaler.zpa.models.cloudbrowserisolation import CBIBanner
from zscaler.utils import format_url, snake_to_camel


class CloudBrowserIsolationAPI(APIClient):
    """
    A Client object for the Cloud Browser Isolation Banners resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_cbi_banners(self) -> tuple:
        """
        Returns a list of all cloud browser isolation banners.

        Returns:
            tuple: A tuple containing a list of `CBIBanner` instances, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/banners", api_version="cbiconfig_v1")

        # Prepare request
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, CBIBanner)

        if error:
            return (None, response, error)

        # Parse the response into CBIBanner instances
        try:
            result = [CBIBanner(self.form_response_body(item)) for item in response.get_body()]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_cbi_banner(self, banner_id: str, **kwargs) -> tuple:
        """
        Returns information on the specified cloud browser isolation banner.

        Args:
            banner_id (str): The unique identifier for the cloud browser isolation banner.

        Returns:
            tuple: A tuple containing the `CBIBanner` instance, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /banners/{banner_id}
            """,
            api_version="cbiconfig_v1",
        )

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBIBanner)
        if error:
            return (None, response, error)

        return (CBIBanner(response.get_body()), response, None)

    def add_cbi_banner(self, name: str, banner: bool, **kwargs) -> tuple:
        """
        Adds a new cloud browser isolation banner.

        Args:
            name (str): The name of the new cloud browser isolation banner.
            banner (bool): Whether to enable the cloud browser isolation banner.

        Returns:
            tuple: A tuple containing the `CBIBanner` instance, response object, and error if any.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /banners
        """,
            api_version="cbiconfig_v1",
        )

        payload = {
            "name": name,
            "banner": banner,
        }

        # Add optional parameters to the payload
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBIBanner)
        if error:
            return (None, response, error)

        return (CBIBanner(response.get_body()), response, None)

    def update_cbi_banner(self, banner_id: str, **kwargs) -> tuple:
        """
        Updates an existing cloud browser isolation banner.

        Args:
            banner_id (str): The unique identifier of the cloud browser isolation banner.

        Returns:
            tuple: A tuple containing the `CBIBanner` instance, response object, and error if any.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /banners/{banner_id}
            """,
            api_version="cbiconfig_v1",
        )

        # Get current banner data and update it
        current_banner, response, error = self.get_cbi_banner(banner_id)
        if error:
            return (None, response, error)

        payload = current_banner.request_format()
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBIBanner)
        if error:
            return (None, response, error)

        return (CBIBanner(response.get_body()), response, None)

    def delete_cbi_banner(self, banner_id: str) -> tuple:
        """
        Deletes the specified cloud browser isolation banner.

        Args:
            banner_id (str): The unique identifier for the cloud browser isolation banner to be deleted.

        Returns:
            tuple: A tuple containing the response object and error if any.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /banners/{banner_id}
            """,
            api_version="cbiconfig_v1",
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return (None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, error)

        return (response, None)

    def list_cbi_certificates(self) -> tuple:
        """
        Returns a list of all cloud browser isolation certificates.

        Returns:
            tuple: A tuple containing a list of `CBICertificate` instances, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/certificates", api_version="cbiconfig_v1")

        # Prepare request
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, CBICertificate)

        if error:
            return (None, response, error)

        # Parse the response into CBICertificate instances
        try:
            result = [CBICertificate(self.form_response_body(item)) for item in response.get_body()]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_cbi_certificate(self, certificate_id: str, **kwargs) -> tuple:
        """
        Returns information on the specified cloud browser isolation certificate.

        Args:
            certificate_id (str): The unique identifier for the cloud browser isolation certificate.

        Returns:
            tuple: A tuple containing the `CBICertificate` instance, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /certificates/{certificate_id}
            """,
            api_version="cbiconfig_v1",
        )

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBICertificate)
        if error:
            return (None, response, error)

        return (CBICertificate(response.get_body()), response, None)

    def add_cbi_certificate(self, name: str, pem: str, **kwargs) -> tuple:
        """
        Adds a new cloud browser isolation certificate.

        Args:
            name (str): The name of the new cloud browser isolation certificate.
            pem (str): The content of the certificate in PEM format.

        Returns:
            tuple: A tuple containing the `CBICertificate` instance, response object, and error if any.

        Examples:
            Creating a Cloud browser isolation with the minimum required parameters:

            >>> zpa.isolation.add_certificate(
            ...   name='new_certificate',
            ...   pem=("-----BEGIN CERTIFICATE-----\\n"
            ...              "nMIIF2DCCA8CgAwIBAgIBATANBgkqhkiG==\\n"
            ...              "-----END CERTIFICATE-----"),
            )

        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /certificates
            """,
            api_version="cbiconfig_v1",
        )

        payload = {
            "name": name,
            "pem": pem,
        }

        # Add optional parameters to payload
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBICertificate)
        if error:
            return (None, response, error)

        return (CBICertificate(response.get_body()), response, None)

    def update_cbi_certificate(self, certificate_id: str, **kwargs) -> tuple:
        """
        Updates an existing cloud browser isolation certificate.

        Args:
            certificate_id (str): The unique identifier for the cloud browser isolation certificate.

        Returns:
            tuple: A tuple containing the `CBICertificate` instance, response object, and error if any.

        Examples:
            Updating the name of a Cloud browser isolation:

            >>> zpa.isolation.update_certificate(
            ...   name='new_certificate',
            ...   pem=("-----BEGIN CERTIFICATE-----\\n"
            ...              "MIIFNzCCBIHNIHIO==\\n"
            ...              "-----END CERTIFICATE-----"),
            )
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /certificates/{certificate_id}
            """,
            api_version="cbiconfig_v1",
        )

        # Get current certificate data and update it
        current_certificate, response, error = self.get_cbi_certificate(certificate_id)
        if error:
            return (None, response, error)

        payload = current_certificate.request_format()
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBICertificate)
        if error:
            return (None, response, error)

        return (CBICertificate(response.get_body()), response, None)

    def delete_cbi_certificate(self, certificate_id: str) -> tuple:
        """
        Deletes the specified cloud browser isolation certificate.

        Args:
            certificate_id (str): The unique identifier for the cloud browser isolation certificate.

        Returns:
            tuple: A tuple containing the response object and error if any.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /certificates/{certificate_id}
            """,
            api_version="cbiconfig_v1",
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return (None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, error)

        return (response, None)

    def list_cbi_profiles(self) -> tuple:
        """
        Enumerates CBI Profiles in your organization with pagination.
        A subset of connector groups can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of CBI Profiles instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/isolation/profiles")

        # Prepare request
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, CBIProfile)

        if error:
            return (None, response, error)

        # Parse the response into CBIProfile instances
        try:
            result = [CBIProfile(self.form_response_body(item)) for item in response.get_body()]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_cbi_profile(self, profile_id: str, **kwargs) -> tuple:
        """
        Returns information on the specified cloud browser isolation profile.

        Args:
            profile_id (str): The unique identifier for the cloud browser isolation profile.

        Returns:
            tuple: A tuple containing the `CBIProfile` instance, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/profiles/{profile_id}", api_version="cbiconfig_v1")

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBIProfile)
        if error:
            return (None, response, error)

        return (CBIProfile(response.get_body()), response, None)

    def get_cbi_profile_by_name(self, name: str) -> tuple:
        """
        Retrieves a specific isolation profile by its name.

        Args:
            name (str): The name of the isolation profile to search for.

        Returns:
            tuple: A tuple containing the `CBIProfile` instance, response object, and error if any.
        """
        profiles, response, error = self.list_cbi_profiles()
        if error:
            return (None, response, error)

        for profile in profiles:
            if profile.name == name:
                return (profile, response, None)

        return (None, response, f"Profile with name {name} not found")

    def list_cbi_zpa_profiles(self) -> tuple:
        """
        Returns a list of all cloud browser isolation ZPA profiles, with options to filter by disabled status and scope.

        Args:
            show_disabled (bool, optional): If set to True, the response includes disabled profiles.
            scope_id (str, optional): The unique identifier of the scope of the tenant to filter the profiles.

        Returns:
            tuple: A tuple containing a list of `ZPAProfile` instances, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/isolation/zpaprofiles", api_version="cbiconfig_v1")

        # Prepare request
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, ZPACBIProfile)

        if error:
            return (None, response, error)

        # Parse the response into ZPACBIProfile instances
        try:
            result = [ZPACBIProfile(self.form_response_body(item)) for item in response.get_body()]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def add_cbi_profile(self, name: str, region_ids: list, certificate_ids: list, **kwargs) -> tuple:
        """
        Adds a new cloud browser isolation profile to the Zscaler platform.

        Args:
            name (str): The name of the new cloud browser isolation profile.
            region_ids (list): List of region IDs. Requires at least 2 region IDs.
            certificate_ids (list): List of certificate IDs associated with the profile.

        Keyword Args:
            description (str, optional): A brief description of the security profile.
            is_default (bool, optional): Indicates if this profile should be set as the default for new users.
            banner_id (str, optional): The unique identifier for a custom banner displayed in the isolation session.
            security_controls (dict, optional): Specifies the cloud browser isolation security settings.

                - document_viewer (bool): Enable or disable document viewing capabilities
                - allow_printing (bool): Allow or restrict printing of documents
                - watermark (dict): Configuration for watermarking documents displayed in the browser:
                    - enabled (bool): Enable or disable watermarking
                    - show_user_id (bool): Display user ID on the watermark.
                    - show_timestamp (bool): Include a timestamp in the watermark.
                    - show_message (bool): Include a custom message in the watermark.
                    - message (str): The custom message to display if 'show_message' is True.

                - flattened_pdf (bool): Specify whether PDFs should be flattened.
                - upload_download (str): Control upload and download capabilities ('all', 'none', or other configurations).
                - restrict_keystrokes (bool): Restrict the use of keystrokes within the isolation session.
                - copy_paste (str): Control copy and paste capabilities ('all', 'none', or specific configurations).
                - local_render (bool): Enable or disable local rendering of web content.

            debug_mode (dict, optional): Debug mode settings that may include logging and error tracking configurations.

                - allowed (bool, optional): Allow debug mode
                - file_password (str, Optional): Optional password to debug files when this mode is enabled.

            user_experience (dict, optional): Settings that affect how end-users interact with the isolated browser.

                - forward_to_zia (dict): Configuration for forwarding traffic to ZIA:
                    - enabled (bool): Enable or disable forwarding.
                    - organization_id (str): Organization ID to use for forwarding.
                    - cloud_name (str): Name of the Zscaler cloud.
                    - pac_file_url (str): URL to the PAC file.
                - browser_in_browser (bool): Enable or disable the use of a browser within the isolated browser.
                - persist_isolation_bar (bool): Specify whether the isolation bar should remain visible.
                - session_persistence (bool): Enable or disable session persistence across browser restarts.

        Returns:
            tuple: A tuple containing the `CBIProfile` instance, response object, and error if any.
        Examples:
            Creating a security profile with required and optional parameters:

            >>> zpa.cbi_profile.add_cbi_profile(
            ...   name='Add_CBI_Profile',
            ...   region_ids=["dc75dc8d-a713-49aa-821e-eb35da523cc2", "1a2cd1bc-b8e0-466b-96ad-fbe44832e1c7"],
            ...   certificate_ids=["87122222-457f-11ed-b878-0242ac120002"],
            ...   description='Description of Add_CBI_Profile',
            ...   security_controls={
            ...       "document_viewer": True,
            ...       "allow_printing": True,
            ...       "watermark": {
            ...           "enabled": True,
            ...           "show_user_id": True,
            ...           "show_timestamp": True,
            ...           "show_message": True,
            ...           "message": "Confidential"
            ...       },
            ...       "flattened_pdf": False,
            ...       "upload_download": "all",
            ...       "restrict_keystrokes": True,
            ...       "copy_paste": "all",
            ...       "local_render": True
            ...   },
            ...   debug_mode={
            ...       "allowed": True,
            ...       "file_password": ""
            ...   },
            ...   user_experience={
            ...       "forward_to_zia": {
            ...           "enabled": True,
            ...           "organization_id": "44772833",
            ...           "cloud_name": "example_cloud",
            ...           "pac_file_url": "https://pac.example_cloud/proxy.pac"
            ...       },
            ...       "browser_in_browser": True,
            ...       "persist_isolation_bar": True,
            ...       "session_persistence": True
            ...   },
            ...   banner_id="97f339f6-9f85-40fb-8b76-f62cdf8f795c"
            ... )

        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_endpoint}/profiles", api_version="cbiconfig_v1")

        payload = {
            "name": name,
            "regionIds": region_ids,
            "certificateIds": certificate_ids,
        }

        # Add optional parameters to the payload
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBIProfile)
        if error:
            return (None, response, error)

        return (CBIProfile(response.get_body()), response, None)

    def update_cbi_profile(self, profile_id: str, **kwargs) -> tuple:
        """
        Updates an existing cloud browser isolation profile.

        Args:
            profile_id (str):
                The unique identifier for the cloud browser isolation profile to be updated.
            **kwargs: Optional keyword args.

        Keyword Args:
            description (str, optional): A brief description of the security profile.
            is_default (bool, optional): Indicates if this profile should be set as the default for new users.
            banner_id (str, optional): The unique identifier for a custom banner displayed in the isolation session.
            security_controls (dict, optional): Specifies the cloud browser isolation security settings.

                - document_viewer (bool): Enable or disable document viewing capabilities
                - allow_printing (bool): Allow or restrict printing of documents
                - watermark (dict): Configuration for watermarking documents displayed in the browser:
                    - enabled (bool): Enable or disable watermarking
                    - show_user_id (bool): Display user ID on the watermark.
                    - show_timestamp (bool): Include a timestamp in the watermark.
                    - show_message (bool): Include a custom message in the watermark.
                    - message (str): The custom message to display if 'show_message' is True.

                - flattened_pdf (bool): Specify whether PDFs should be flattened.
                - upload_download (str): Control upload and download capabilities ('all', 'none', or other configurations).
                - restrict_keystrokes (bool): Restrict the use of keystrokes within the isolation session.
                - copy_paste (str): Control copy and paste capabilities ('all', 'none', or specific configurations).
                - local_render (bool): Enable or disable local rendering of web content.

            debug_mode (dict, optional): Debug mode settings that may include logging and error tracking configurations.

                - allowed (bool, optional): Allow debug mode
                - file_password (str, Optional): Optional password to debug files when this mode is enabled.

            user_experience (dict, optional): Settings that affect how end-users interact with the isolated browser.

                - forward_to_zia (dict): Configuration for forwarding traffic to ZIA:
                    - enabled (bool): Enable or disable forwarding.
                    - organization_id (str): Organization ID to use for forwarding.
                    - cloud_name (str): Name of the Zscaler cloud.
                    - pac_file_url (str): URL to the PAC file.

                - browser_in_browser (bool): Enable or disable the use of a browser within the isolated browser.
                - persist_isolation_bar (bool): Specify whether the isolation bar should remain visible.
                - session_persistence (bool): Enable or disable session persistence across browser restarts.

        Returns:
            tuple: A tuple containing the `CBIProfile` instance, response object, and error if any.

        Examples:
            Updating the name and description of a cloud browser isolation profile:

            >>> zpa.cbi_profile.update_cbi_profile(
            ...   profile_id='1beed6be-eb22-4328-92f2-fbe73fd6e5c7',
            ...   name='CBI_Profile_Update'
            ...   description='CBI_Profile_Update'
            )
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_endpoint}/profiles{profile_id}", api_version="cbiconfig_v1")

        # Get the current profile and update it
        current_profile, response, error = self.get_cbi_profile(profile_id)
        if error:
            return (None, response, error)

        payload = current_profile.request_format()
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, CBIProfile)
        if error:
            return (None, response, error)

        return (CBIProfile(response.get_body()), response, None)

    def delete_cbi_profile(self, profile_id: str) -> tuple:
        """
        Deletes the specified cloud browser isolation profile.

        Args:
            profile_id (str): The unique identifier of the cloud browser isolation profile.

        Returns:
            tuple: A tuple containing the response object and error if any.
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_endpoint}/profiles{profile_id}", api_version="cbiconfig_v1")

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return (None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, error)

        return (response, None)

    def list_cbi_regions(self, **kwargs) -> list:
        """
        Returns a list of all cloud browser isolation regions.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): Specifies the page size. The default size is 20, but the maximum size is 500.
            search (str, optional): The search string used to match against features and fields.
            **keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of CBIRegion instances.

        Examples:
            >>> for region in zpa.isolation.list_cbi_regions():
            ...    pprint(region)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/regions", api_version="cbiconfig_v1")

        # Prepare request
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, CBIRegion)

        if error:
            return (None, response, error)

        # Parse the response into CBIRegion instances
        try:
            result = [CBIRegion(self.form_response_body(item)) for item in response.get_body()]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_cbi_region(self, region_id: str) -> tuple:
        """
        Returns information on the specified cloud browser isolation region by ID.

        Args:
            region_id (str): The unique identifier for the cloud browser isolation region.

        Returns:
            tuple: A tuple containing the `CBIRegion` instance, response object, and error if any.

        Examples:
            >>> region = zpa.isolation.get_cbi_region('dc75dc8d-a713-49aa-821e-eb35da523cc2')
            >>> pprint(region)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /regions/{region_id}
            """,
            api_version="cbiconfig_v1",
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None, None, error

        response, error = self._request_executor.execute(request, CBIRegion)
        if error:
            return None, response, error

        return CBIRegion(response.get_body()), response, None
