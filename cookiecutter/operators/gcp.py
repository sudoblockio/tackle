# -*- coding: utf-8 -*-

"""GCP Operators."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from googleapiclient.discovery import build

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class GcpRegionsOperator(BaseOperator):
    """Operator retrieving GCP regions.

    :return: List of regions
    """

    type = 'gcp_regions'

    def __init__(self, *args, **kwargs):  # noqa
        super(GcpRegionsOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        client = build('compute', 'v1')

        regions = [
            item['name']
            for item in client.regions()
            .list(project=self.operator_dict['gcp_project'])
            .execute()['items']
        ]

        return regions
