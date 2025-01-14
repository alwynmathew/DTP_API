# -*- coding: utf-8 -*-`

#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import json
import uuid

import requests
import validators

from helpers import logger_global


class FetchAPI:
    """
    Mixin fetch API class contains all fetch methods.

    Methods
    -------
    get_uuid_for_iri(url)
        returns UUID
    fetch_node_with_iri(iri)
        returns dictionary created from JSON
    fetch_element_nodes(url)
        returns dictionary created from JSON
    fetch_asdesigned_nodes(url)
        returns dictionary created from JSON
    fetch_asbuilt_nodes(url)
        returns dictionary created from JSON
    fetch_construction_nodes(url)
        returns dictionary created from JSON
    fetch_workpackage_nodes(url)
        returns dictionary created from JSON
    fetch_workpackage_connected_activity_nodes(wp_node_iri, url)
        returns dictionary created from JSON
    fetch_asperformed_connected_asdesigned_oper_nodes(asdesigned_node_iri, url)
        returns dictionary created from JSON
    fetch_activity_connected_task_nodes(activity_node_iri, url)
        returns dictionary created from JSON
    fetch_elements_connected_task_nodes(task_node_iri, url)
        returns dictionary created from JSON
    fetch_activity_nodes(url)
        returns dictionary created from JSON
    fetch_asbuilt_connected_asdesigned_nodes(asbuilt_node_iri)
        returns dictionary created from JSON
    fetch_asdesigned_connected_task_nodes(asdesigned_node_iri, url)
        returns dictionary created from JSON
    fetch_oper_connected_activity_nodes(oper_node_iri, url)
        returns dictionary created from JSON
    fetch_task_connected_activity_nodes(task_node_iri, url)
        returns dictionary created from JSON
    fetch_activity_connected_workpackage_nodes(activity_node_iri, url)
        returns dictionary created from JSON
    fetch_workpackage_connected_schedule_nodes(workpkg_node_iri, url)
        returns dictionary created from JSON
    fetch_constr_connected_oper_nodes(constr_node_iri, url)
        returns dictionary created from JSON
    fetch_oper_connected_action_nodes(oper_node_iri, url)
        returns dictionary created from JSON
    fetch_action_connected_asbuilt_nodes(action_node_iri, url)
        returns dictionary created from JSON
    fetch_blobs_for_node(node_uuid)
        returns dictionary created from JSON
    download_blob_as_text(blob_uuid)
        returns file as a string-stream
    """

    def get_uuid_for_iri(self, iri):
        """
        The method returns UUID for a valid IRI.

        Parameters
        ----------
        iri : str, obligatory
            a valid IRI for which to return the corresponding UUID

        Raises
        ------
        - it can raise an exception if the request has not been successful, or
        - if the IRI is not a valid URI

        Returns
        ------
        str
            uuid
        """

        if not validators.url(iri):
            raise Exception("Sorry, the IRI is not a valid URI.")

        payload = json.dumps({
            "query": {
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": iri
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.DTP_CONFIG.get_token()
        }

        session = requests.Session()
        req = requests.Request("POST", self.DTP_CONFIG.get_api_url('get_find_elements'), headers=headers, data=payload)
        prepared = req.prepare()

        logger_global.info('HTTP request: \n' + self.pretty_http_request_to_string(prepared))

        if not self.simulation_mode:
            response = session.send(prepared)
            logger_global.info('Response code: ' + str(response.status_code))
            if response.ok:
                return response.json()['items'][0]['_uuid']
            else:
                logger_global.error(
                    "Something went wrong, no UUID from the give IRI. Status code: " + str(response.status_code))
                raise Exception(
                    "Something went wrong, no UUID from the give IRI. Status code: " + str(response.status_code))
        else:
            return str(uuid.uuid4())

    def fetch_node_with_iri(self, node_iri):
        """
        The method queries nodes with given iri

        Parameters
        ----------
        node_iri : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain nodes of the type element.
        """

        payload = json.dumps({
            "query": {
                "$domain": self.DTP_CONFIG.get_domain(),
                "iri": node_iri
            }
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements')
        return self.post_general_request(payload, req_url).json()

    def fetch_element_nodes(self, *additional_filter, url=None):
        """
        The method queries nodes of type elements from the platform.

        Parameters
        ----------
        url : str, optional
            used to fetch a next page
        additional_filter: tuple, optional
            additional filter

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain nodes of the type element.
        """
        query_dict = {
            "$domain": self.DTP_CONFIG.get_domain(),
            "$classes": {
                "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                "$inheritance": True
            }
        }

        if len(additional_filter) == 2:
            field_name, field_value = additional_filter
            query_dict[field_name] = field_value
        elif len(additional_filter) == 1:
            url = additional_filter
        else:
            raise TypeError(f"Maximum additional_filter length is two but got {len(additional_filter)}")

        payload = json.dumps({
            "query": query_dict
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_asdesigned_nodes(self, *additional_filter, url=None):
        """
        The method queries As-Designed nodes from the platform.

        Parameters
        ----------
        url : str, optional
            used to fetch a next page
        additional_filter: tuple, optional
            additional filter

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain nodes that are of type As-Designed.
        """

        query_dict = {
            "$domain": self.DTP_CONFIG.get_domain(),
            "$classes": {
                "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                "$inheritance": True
            },
            self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): True
        }

        if len(additional_filter) == 2:
            field_name, field_value = additional_filter
            query_dict[field_name] = field_value
        elif len(additional_filter) == 1:
            url = additional_filter
        else:
            raise TypeError(f"Maximum additional_filter length is two but got {len(additional_filter)}")

        payload = json.dumps({
            "query": query_dict
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_asbuilt_nodes(self, *additional_filter, url=None):
        """
        The method queries As-Built nodes from the platform.

        Parameters
        ----------
        url : str, optional
            used to fetch a next page
        additional_filter: tuple, optional
            additional filter

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain elements that are of type As-Built.
        """

        query_dict = {
            "$domain": self.DTP_CONFIG.get_domain(),
            "$classes": {
                "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                "$inheritance": True
            },
            self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False
        }

        if len(additional_filter) == 2:
            field_name, field_value = additional_filter
            query_dict[field_name] = field_value
        elif len(additional_filter) == 1:
            url = additional_filter
        else:
            raise TypeError(f"Maximum additional_filter length is two but got {len(additional_filter)}")

        payload = json.dumps({
            "query": query_dict
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_construction_nodes(self, url=None):
        """
        The method queries construction nodes from the platform.

        Parameters
        ----------
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain elements that are of type As-Built.
        """

        payload = json.dumps({
            "query": {
                "$domain": self.DTP_CONFIG.get_domain(),
                "$classes": {
                    "$contains": self.DTP_CONFIG.get_ontology_uri('asPerformedConstruction'),
                    "$inheritance": True
                }
            }
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_workpackage_nodes(self, url=None):
        """
        The method queries work package nodes from the platform.

        Parameters
        ----------
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain as-planned work package nodes.
        """

        payload = json.dumps({
            "query": {
                "$domain": self.DTP_CONFIG.get_domain(),
                "$classes": {
                    "$contains": self.DTP_CONFIG.get_ontology_uri('workpackage')
                }
            }
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_workpackage_connected_activity_nodes(self, wp_node_iri, url=None):
        """
        The method fetches activity nodes connected to a work package node identified by wp_node_iri

        Parameters
        ----------
        wp_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain activity nodes connected to wp_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": wp_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasActivity'): {
                    "$alias": "activity"
                }
            },
                {
                    "$alias": "activity",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('activity')
                    }
                }
            ],
            "return": "activity"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_activity_connected_task_nodes(self, activity_node_iri, url=None):
        """
        The method fetches task nodes connected to an activity package node identified by activity_node_iri

        Parameters
        ----------
        activity_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain activity nodes connected to wp_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": activity_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasTask'): {
                    "$alias": "task"
                }
            },
                {
                    "$alias": "task",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('task')
                    }
                }
            ],
            "return": "task"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_elements_connected_task_nodes(self, task_node_iri, url=None):
        """
        The method fetches element nodes connected to a task node identified by task_node_iri

        Parameters
        ----------
        task_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain activity nodes connected to wp_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": task_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasTarget'): {
                    "$alias": "element"
                }
            }
            ],
            "return": "element"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_asperformed_connected_asdesigned_nodes(self, asdesigned_node_iri, url=None):
        """
        The method fetches as-performed nodes connected to an as-designed node identified with node_iri

        Parameters
        ----------
        asdesigned_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        int
            return the number of defect nodes connected to the node identified by node_iri
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": asdesigned_node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'): {
                    "$alias": "AsPerformed"
                }
            },
                {
                    "$alias": "AsPerformed",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                        "$inheritance": True
                    }  # ,
                    # this cannot be included because of the missing info for Mislata site
                    # self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False
                }
            ],
            "edge": True,  # TODO: Not sure what 'edge' means in this query
            "return": "AsPerformed"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_asperformed_connected_asdesigned_oper_nodes(self, asdesigned_node_iri, url=None):
        """
        The method fetches as-performed operation nodes connected to an as-designed node identified with node_iri

        Parameters
        ----------
        asdesigned_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        int
            return the number of defect nodes connected to the node identified by node_iri
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": asdesigned_node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'): {
                    "$alias": "AsPerformed"
                }
            },
                {
                    "$alias": "AsPerformed",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('asPerformedOperation')
                    }
                }
            ],
            # "edge": True,  # TODO: Not sure what 'edge' means in this query
            "return": "AsPerformed"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_activity_nodes(self, url=None):
        """
        The method queries activity nodes from the platform.

        Parameters
        ----------
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain as-planned work package nodes.
        """

        payload = json.dumps({
            "query": {
                "$domain": self.DTP_CONFIG.get_domain(),
                "$classes": {
                    "$contains": self.DTP_CONFIG.get_ontology_uri('activity')
                }
            }
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_asbuilt_connected_asdesigned_nodes(self, asbuilt_node_iri, url=None):
        """
        The method fetches as-designed nodes connected to a node identified by node_iri

        Parameters
        ----------
        asbuilt_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain as-designed nodes connected to asbuilt_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": asbuilt_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'): {
                    "$alias": "asdesigned"
                }
            },
                {
                    "$alias": "asdesigned",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                        "$inheritance": True
                    }  # ,
                    # this cannot be included because of the missing info for Mislata site
                    # self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False
                }
            ],
            "edge": True,
            "return": "asdesigned"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_asdesigned_connected_task_nodes(self, asdesigned_node_iri, url=None):
        """
        The method fetches task nodes connected to a node identified by asdesigned_node_iri

        Parameters
        ----------
        asdesigned_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain task nodes connected to asdesigned_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": asdesigned_node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('hasTarget'): {
                    "$alias": "tasks"
                }
            },
                {
                    "$alias": "tasks",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('task'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "tasks"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_oper_connected_activity_nodes(self, oper_node_iri, url=None):
        """
        The method fetches activity nodes connected to an operation node identified by oper_node_iri

        Parameters
        ----------
        oper_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain activity nodes connected to oper_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": oper_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'): {
                    "$alias": "hasActivity"
                }
            },
                {
                    "$alias": "hasActivity",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('activity'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasActivity"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_task_connected_activity_nodes(self, task_node_iri, url=None):
        """
        The method fetches activity nodes connected to a node identified by task_node_iri

        Parameters
        ----------
        task_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain activity nodes connected to task_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": task_node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('hasTask'): {
                    "$alias": "hasActivity"
                }
            },
                {
                    "$alias": "hasActivity",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('activity'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasActivity"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_activity_connected_workpackage_nodes(self, activity_node_iri, url=None):
        """
        The method fetches workpackage nodes connected to a node identified by activity_node_iri

        Parameters
        ----------
        activity_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain workpackage nodes connected to activity_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": activity_node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('hasActivity'): {
                    "$alias": "hasWorkPackage"
                }
            },
                {
                    "$alias": "hasWorkPackage",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('workpackage'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasWorkPackage"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_workpackage_connected_schedule_nodes(self, workpkg_node_iri, url=None):
        """
        The method fetches schedule nodes connected to a node identified by workpkg_node_iri

        Parameters
        ----------
        workpkg_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain workpackage nodes connected to activity_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": workpkg_node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('hasWorkPackage'): {
                    "$alias": "hasSchedule"
                }
            },
                {
                    "$alias": "hasSchedule",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('constructionSchedule'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasSchedule"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_constr_connected_oper_nodes(self, constr_node_iri, url=None):
        """
        The method fetches operation nodes connected to a node identified by constr_node_iri

        Parameters
        ----------
        constr_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain operation nodes connected to constr_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": constr_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasOperation'): {
                    "$alias": "hasOperation"
                }
            },
                {
                    "$alias": "hasOperation",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('asPerformedOperation'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasOperation"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_oper_connected_action_nodes(self, oper_node_iri, url=None):
        """
        The method fetches action nodes connected to a node identified by oper_node_iri

        Parameters
        ----------
        oper_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain action nodes connected to oper_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": oper_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasAction'): {
                    "$alias": "hasAction"
                }
            },
                {
                    "$alias": "hasAction",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('asPerformedAction'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasAction"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_action_connected_asbuilt_nodes(self, action_node_iri, url=None):
        """
        The method fetches as-built nodes connected to a node identified by action_node_iri

        Parameters
        ----------
        action_node_iri : str, obligatory
            a valid IRI of a node.
        url : str, optional
            used to fetch a next page

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain asbuilt nodes connected to action_node_iri.
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": action_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasTarget'): {
                    "$alias": "asbuilt"
                }
            },
                {
                    "$alias": "asbuilt",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                        "$inheritance": True
                    },
                    self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False
                }
            ],
            "edge": True,
            "return": "asbuilt"
        })

        req_url = self.DTP_CONFIG.get_api_url('get_find_elements') if not url else url
        return self.post_general_request(payload, req_url).json()

    def fetch_blobs_for_node(self, node_uuid):
        """
        The method queries blobs for a given node.

        Parameters
        ----------
        node_uuid : str, obligatory
            UUID of a node for which we want to obtain blobs.

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        dictionary
            JSON mapped to a dictionary. The data contain blobs for the corresponding element.
        """

        payload = ""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.DTP_CONFIG.get_token()
        }

        session = requests.Session()
        req = requests.Request("GET", self.DTP_CONFIG.get_api_url('get_blobs_per_element', node_uuid), headers=headers,
                               data=payload)
        prepared = req.prepare()

        logger_global.info('HTTP request: \n' + self.pretty_http_request_to_string(prepared))

        response = session.send(prepared)
        logger_global.info('Response code: ' + str(response.status_code))

        if response.ok:
            return response.json()
        else:
            logger_global.error(
                "The response from the DTP is an error. Check the dev token and/or the domain. Status code: " + str(
                    response.status_code))
            raise Exception(
                "The response from the DTP is an error. Check the dev token and/or the domain. Status code: " + str(
                    response.status_code))

    def download_blob_as_text(self, blob_uuid):
        """
        The method downloads a blob.

        Parameters
        ----------
        blob_uuid : str, obligatory
            UUID of, a blob which should be downloaded.

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        str
            file as a string-stream
        """

        payload = ""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.DTP_CONFIG.get_token()
        }

        session = requests.Session()
        req = requests.Request("GET", self.DTP_CONFIG.get_api_url('download_blob', blob_uuid), headers=headers,
                               data=payload)
        prepared = req.prepare()

        logger_global.info('HTTP request: \n' + self.pretty_http_request_to_string(prepared))

        response = session.send(prepared)
        logger_global.info('Response code: ' + str(response.status_code))

        if response.ok:
            return response.text
        else:
            logger_global.error("The blob cannot be fetched. Status code: " + str(response.status_code))
            raise Exception("The blob cannot be fetched. Status code: " + str(response.status_code))
