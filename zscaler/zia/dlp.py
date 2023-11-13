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


from box import Box, BoxList
from requests import Response
from zscaler.utils import snake_to_camel
from zscaler.zia import ZIAClient

class DLPAPI:

    def __init__(self, client: ZIAClient):
        self.rest = client

    def add_dict(self, name: str, match_type: str, **kwargs) -> Box:
        """
        Add a new Patterns and Phrases DLP Dictionary to ZIA.

        Args:
            name (str): The name of the DLP Dictionary.
            match_type (str): The DLP custom phrase/pattern match type. Accepted values are ``all`` or ``any``.
            **kwargs: Optional keyword args.

        Keyword Args:
            description (str): Additional information about the DLP Dictionary.
            phrases (list):
                A list of DLP phrases, with each phrase provided by a tuple following the convention
                (`action`, `pattern`). Accepted actions are ``all`` or ``unique``. E.g.

                .. code-block:: python

                    ('all', 'TOP SECRET')
                    ('unique', 'COMMERCIAL-IN-CONFIDENCE')

            patterns (list):
                A list of DLP patterns, with each pattern provided by a tuple following the convention
                (`action`, `pattern`). Accepted actions are ``all`` or ``unique``. E.g.

                .. code-block:: python

                    ('all', '\d{2} \d{3} \d{3} \d{3}')
                    ('unique', '[A-Z]{6}[A-Z0-9]{2,5}')

        Returns:
            :obj:`Box`: The newly created DLP Dictionary resource record.

        Examples:
            Match text found that contains an IPv4 address using patterns:

            >>> zia.dlp.add_dict(name='IPv4 Addresses',
            ...                description='Matches IPv4 address pattern.',
            ...                match_type='all',
            ...                patterns=[
            ...                    ('all', '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/(\d|[1-2]\d|3[0-2]))?')
            ...                ]))

            Match text found that contains government document caveats using phrases.

            >>> zia.dlp.add_dict(name='Gov Document Caveats',
            ...                description='Matches government classification caveats.',
            ...                match_type='any',
            ...                phrases=[
            ...                    ('all', 'TOP SECRET'),
            ...                    ('all', 'SECRET'),
            ...                    ('all', 'CONFIDENTIAL')
            ...                ]))

            Match text found that meets the criteria for a Secret Project's document markings using phrases and
            patterns:

            >>> zia.dlp.add_dict(name='Secret Project Documents',
            ...                description='Matches documents created for the Secret Project.',
            ...                match_type='any',
            ...                phrases=[
            ...                    ('all', 'Project Umbrella'),
            ...                    ('all', 'UMBRELLA')
            ...                ],
            ...                patterns=[
            ...                    ('unique', '\d{1,2}-\d{1,2}-[A-Z]{5}')
            ...                ]))

        """

        payload = {
            "name": name,
            "dictionaryType": "PATTERNS_AND_PHRASES",
        }

        # Simplify Zscaler's required values for our users.
        if match_type == "all":
            payload["customPhraseMatchType"] = "MATCH_ALL_CUSTOM_PHRASE_PATTERN_DICTIONARY"
        elif match_type == "any":
            payload["customPhraseMatchType"] = "MATCH_ANY_CUSTOM_PHRASE_PATTERN_DICTIONARY"
        else:
            raise ValueError

        if kwargs.get("patterns"):
            for pattern in kwargs.pop("patterns"):
                payload.setdefault("patterns", []).append(
                    {
                        "action": f"PATTERN_COUNT_TYPE_{pattern[0].upper()}",
                        "pattern": pattern[1],
                    }
                )

        if kwargs.get("phrases"):
            for phrase in kwargs.pop("phrases"):
                payload.setdefault("phrases", []).append(
                    {
                        "action": f"PHRASE_COUNT_TYPE_{phrase[0].upper()}",
                        "phrase": phrase[1],
                    }
                )

        # Update payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        response = self.rest.post(path="dlpDictionaries", json=payload)
        if isinstance(response, Response):
            return None
        return response

    def update_dict(self, dict_id: str, **kwargs) -> Box:
        """
        Updates the specified DLP Dictionary.

        Args:
            dict_id (str): The unique id of the DLP Dictionary.
            **kwargs: Optional keyword args.

        Keyword Args:
            description (str): Additional information about the DLP Dictionary.
            match_type (str): The DLP custom phrase/pattern match type. Accepted values are ``all`` or ``any``.
            name (str): The name of the DLP Dictionary.
            phrases (list):
                A list of DLP phrases, with each phrase provided by a tuple following the convention
                (`action`, `pattern`). Accepted actions are ``all`` or ``unique``. E.g.

                .. code-block:: python

                    ('all', 'TOP SECRET')
                    ('unique', 'COMMERCIAL-IN-CONFIDENCE')

            patterns (list):
                A list of DLP pattersn, with each pattern provided by a tuple following the convention
                (`action`, `pattern`). Accepted actions are ``all`` or ``unique``. E.g.

                .. code-block:: python

                    ('all', '\d{2} \d{3} \d{3} \d{3}')
                    ('unique', '[A-Z]{6}[A-Z0-9]{2,5}')

        Returns:
            :obj:`Box`: The updated DLP Dictionary resource record.

        Examples:
            Update the name of a DLP Dictionary:

            >>> zia.dlp.update_dict('3',
            ...                name='IPv4 and IPv6 Addresses')

            Update the description and phrases for a DLP Dictionary.

            >>> zia.dlp.update_dict('4',
            ...        description='Updated government caveats.'
            ...        phrases=[
            ...                    ('all', 'TOP SECRET'),
            ...                    ('all', 'SECRET'),
            ...                    ('all', 'PROTECTED')
            ...                ])

        """
        # Set payload to value of existing record
        payload = {snake_to_camel(k): v for k, v in self.get_dict(dict_id).items()}

        if kwargs.get("match_type"):
            match_type = kwargs.pop("match_type")
            if match_type == "all":
                payload["customPhraseMatchType"] = "MATCH_ALL_CUSTOM_PHRASE_PATTERN_DICTIONARY"
            elif match_type == "any":
                payload["customPhraseMatchType"] = "MATCH_ANY_CUSTOM_PHRASE_PATTERN_DICTIONARY"
            else:
                raise ValueError

        # If patterns or phrases provided, overwrite existing values
        if kwargs.get("patterns"):
            payload["patterns"] = []
            for pattern in kwargs.pop("patterns"):
                payload.setdefault("patterns", []).append(
                    {
                        "action": f"PATTERN_COUNT_TYPE_{pattern[0].upper()}",
                        "pattern": pattern[1],
                    }
                )

        if kwargs.get("phrases"):
            payload["phrases"] = []
            for phrase in kwargs.pop("phrases"):
                payload["phrases"].append(
                    {
                        "action": f"PHRASE_COUNT_TYPE_{phrase[0].upper()}",
                        "phrase": phrase[1],
                    }
                )

        # Update payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        response = self.rest.put("/dlpDictionaries/%s" % (dict_id), json=payload)
        if not isinstance(response, Response):
            return self.get_dict(dict_id)

    def list_dicts(self, query: str = None) -> BoxList:
        """
        Returns a list of all custom and predefined ZIA DLP Dictionaries.

        Args:
            query (str): A search string used to match against a DLP dictionary's name or description attributes.

        Returns:
            :obj:`BoxList`: A list containing ZIA DLP Dictionaries.

        Examples:
            Print all dictionaries

            >>> for dictionary in zia.dlp.list_dicts():
            ...    pprint(dictionary)

            Print dictionaries that match the name or description 'GDPR'

            >>> pprint(zia.dlp.list_dicts('GDPR'))

        """
        payload = {"search": query}
        list = self.rest.get(path="/dlpDictionaries", params=payload)
        if isinstance(list, Response):
            return None
        return list

    def get_dict(self, dict_id: str) -> Box:
        """
        Returns the DLP Dictionary that matches the specified DLP Dictionary id.

        Args:
            dict_id (str): The unique id for the DLP Dictionary.

        Returns:
            :obj:`Box`: The ZIA DLP Dictionary resource record.

        Examples:
            >>> pprint(zia.dlp.get_dict('3'))

        """
        response = self.rest.get("/dlpDictionaries/%s" % (dict_id))
        if isinstance(response, Response):
            return None
        return response

    def delete_dict(self, dict_id: str) -> int:
        """
        Deletes the DLP Dictionary that matches the specified DLP Dictionary id.

        Args:
            dict_id (str): The unique id for the DLP Dictionary.

        Returns:
            :obj:`int`: The status code for the operation.

        Examples:
            >>> zia.dlp.delete_dict('8')

        """
        response = self.rest.delete("/dlpDictionaries/%s" % (dict_id))
        return response.status_code

    def validate_dict(self, pattern: str) -> Box:
        """
        Validates the provided pattern for usage in a DLP Dictionary.

        Note: The ZIA API documentation doesn't provide information on how to structure a request for this API endpoint.
         This endpoint is returning a valid response but validation isn't failing for obvious wrong patterns. Use at
         own risk.

        Args:
            pattern (str): DLP Pattern for evaluation.

        Returns:
            :obj:`Box`: Information on the provided pattern.

        """
        payload = {"data": pattern}

        response = self.rest.post(path="dlpDictionaries/validateDlpPattern", json=payload)
        if isinstance(response, Response):
            return None
        return response

    # TODO: implemnt the remaining
    def add_dlp_engine(self, name: str, engine_expression=None, custom_dlp_engine=None, description=None) -> Box:
        """
        Adds a new dlp engine.
        ...
        """

        payload = {
            "name": name,
        }

        if engine_expression is not None:
            payload["engineExpression"] = engine_expression

        if custom_dlp_engine is not None:
            payload["customDlpEngine"] = custom_dlp_engine

        if description is not None:
            payload["description"] = description

        # Convert the payload keys to camelCase
        camel_payload = {snake_to_camel(key): value for key, value in payload.items()}

        response = self.rest.post("dlpEngines", json=camel_payload)
        if isinstance(response, Response):
            # this is only true when the creation failed (status code is not 2xx)
            status_code = response.status_code
            # Handle error response
            raise Exception(f"API call failed with status {status_code}: {response.json()}")
        return response

    def update_dlp_engine(self, engine_id: str, **kwargs) -> Box:
        """
        Updates an existing dlp engine.

        Args:
            engine_id (str): The unique ID for the dlp engine that is being updated.
            **kwargs: Optional keyword args.

        Keyword Args:
            name (str): The order of the rule, defaults to adding rule to bottom of list.
            description (str): The admin rank of the rule.
            engine_expression (str, optional):
                The logical expression that defines a DLP engine by combining DLP dictionaries using logical operators, namely All (AND), Any (OR), Exclude (NOT), and Sum (the total number of content matches).
            custom_dlp_engine (bool, optional):
                Indicates whether this is a custom DLP engine. If this value is set to true, the engine is custom.
            description (str, optional):
                The DLP engine description.

        Returns:
            :obj:`Box`: The updated dlp engine resource record.

        Examples:
            Update the dlp engine:

            >>> zia.dlp.add_dlp_engine(name='new_dlp_engine',
            ...    description='TT#1965432122'
                   engine_expression="((D63.S > 1))"
                   custom_dlp_engine=False)

            Update a rule to enable custom dlp engine:

            >>> zia.dlp.add_dlp_engine('976597',
            ...    custom_dlp_engine=True,
                   engine_expression="((D63.S > 1))"
            ...    description="TT#1965232866")

        """

        # Set payload to value of existing record
        payload = {snake_to_camel(k): v for k, v in self.get_dlp_engines(engine_id).items()}

        # Add optional parameters to payload
        for key, value in kwargs.items():
            if key in self._key_id_list:
                payload[snake_to_camel(key)] = []
                for item in value:
                    payload[snake_to_camel(key)].append({"id": item})
            else:
                payload[snake_to_camel(key)] = value

        response = self.rest.put("/dlpEngines/%s" % (engine_id), json=payload)
        if not isinstance(response, Response):
            return self.get_dlp_engines(engine_id)

    def delete_dlp_engine(self, engine_id: str) -> int:
        """
        Deletes the specified dlp engine.

        Args:
            engine_id (str): The unique identifier for the dlp engine.

        Returns:
            :obj:`int`: The status code for the operation.

        Examples:
            >>> zia.dlp.delete_dlp_engine('278454')

        """
        response = self.rest.delete("/dlpEngines/%s" % (engine_id))
        return response.status_code

    def list_dlp_engines(self, query: str = None) -> BoxList:
        """
        Returns the list of ZIA DLP Engines.

        Args:
            query (str): A search string used to match against a DLP Engine's name or description attributes.

        Returns:
            :obj:`BoxList`: A list containing ZIA DLP Engines.

        Examples:
            Print all dlp engines

            >>> for dlp engines in zia.dlp.list_dlp_engines():
            ...    pprint(engine)

            Print engines that match the name or description 'GDPR'

            >>> pprint(zia.dlp.list_dlp_engines('GDPR'))

        """
        payload = {"search": query}
        list = self.rest.get(path="/dlpEngines", params=payload)
        if isinstance(list, Response):
            return None
        return list

    def get_dlp_engines(self, engine_id: str) -> Box:
        """
        Returns the dlp engine details for a given DLP Engine.

        Args:
            engine_id (str): The unique identifier for the DLP Engine.

        Returns:
            :obj:`Box`: The DLP Engine resource record.

        Examples:
            >>> engine = zia.dlp.get_dlp_engines('99999')

        """
        response = self.rest.get("/dlpEngines/%s" % (engine_id))
        if isinstance(response, Response):
            return None
        return response

    def get_dlp_engine_by_name(self, name):
        engines = self.get_dlp_engines()
        for engine in engines:
            if engine.get("name") == name:
                return engine
        return None

    def list_dlp_icap_servers(self, query: str = None) -> BoxList:
        """
        Returns the list of ZIA DLP ICAP Servers.

        Args:
            query (str): A search string used to match against a DLP icap server's name or description attributes.

        Returns:
            :obj:`BoxList`: A list containing ZIA DLP ICAP Servers.

        Examples:
            Print all icap servers

            >>> for dlp icap in zia.dlp.list_dlp_icap_servers():
            ...    pprint(icap)

            Print icaps that match the name or description 'ZS_ICAP'

            >>> pprint(zia.dlp.list_dlp_icap_servers('ZS_ICAP'))

        """
        payload = {"search": query}
        list = self.rest.get(path="/icapServers", params=payload)
        if isinstance(list, Response):
            return None
        return list

    def get_dlp_icap_servers(self, icap_server_id: str) -> Box:
        """
        Returns the dlp icap server details for a given DLP ICAP Server.

        Args:
            icap_server_id (str): The unique identifier for the DLP ICAP Server.

        Returns:
            :obj:`Box`: The DLP ICAP Server resource record.

        Examples:
            >>> icap = zia.dlp.get_dlp_icap_servers('99999')

        """
        response = self.rest.get("/icapServers/%s" % (icap_server_id))
        if isinstance(response, Response):
            return None
        return response

    def list_dlp_incident_receiver(self, query: str = None) -> BoxList:
        """
        Returns the list of ZIA DLP Incident Receiver.

        Args:
            query (str): A search string used to match against a DLP Incident Receiver's name or description attributes.

        Returns:
            :obj:`BoxList`: A list containing ZIA DLP Incident Receiver.

        Examples:
            Print all incident receivers

            >>> for dlp incident receiver in zia.dlp.list_dlp_incident_receiver():
            ...    pprint(receiver)

            Print Incident Receiver that match the name or description 'ZS_INC_RECEIVER_01'

            >>> pprint(zia.dlp.list_dlp_incident_receiver('ZS_INC_RECEIVER_01'))

        """
        payload = {"search": query}
        list = self.rest.get(path="/incidentReceiverServers", params=payload)
        if isinstance(list, Response):
            return None
        return list

    def get_dlp_incident_receiver(self, receiver_id: str) -> Box:
        """
        Returns the dlp incident receiver details for a given DLP Incident Receiver.

        Args:
            receiver_id (str): The unique identifier for the DLP Incident Receiver.

        Returns:
            :obj:`Box`: The DLP Incident Receiver resource record.

        Examples:
            >>> incident_receiver = zia.dlp.get_dlp_incident_receiver('99999')

        """
        response = self.rest.get("/incidentReceiverServers/%s" % (receiver_id))
        if isinstance(response, Response):
            return None
        return response

    def list_dlp_idm_profiles(self, query: str = None) -> BoxList:
        """
        Returns the list of ZIA DLP IDM Profiles.

        Args:
            query (str): A search string used to match against a DLP IDM Profile's name or description attributes.

        Returns:
            :obj:`BoxList`: A list containing ZIA DLP IDM Profiles.

        Examples:
            Print all idm profiles

            >>> for dlp idm in zia.dlp.list_dlp_idm_profiles():
            ...    pprint(idm)

            Print IDM profiles that match the name or description 'IDM_PROFILE_TEMPLATE'

            >>> pprint(zia.dlp.list_dlp_idm_profiles('IDM_PROFILE_TEMPLATE'))

        """
        payload = {"search": query}
        list = self.rest.get(path="/idmprofile", params=payload)
        if isinstance(list, Response):
            return None
        return list

    def get_dlp_idm_profiles(self, profile_id: str) -> Box:
        """
        Returns the dlp idmp profile details for a given DLP IDM Profile.

        Args:
            icap_server_id (str): The unique identifier for the DLP IDM Profile.

        Returns:
            :obj:`Box`: The DLP IDM Profile resource record.

        Examples:
            >>> idm = zia.dlp.get_dlp_idm_profiles('99999')

        """
        response = self.rest.get("/idmprofile/%s" % (profile_id))
        if isinstance(response, Response):
            return None
        return response
