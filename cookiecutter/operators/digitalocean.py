# -*- coding: utf-8 -*-

"""DigitalOcean Operators."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
from dopy.manager import DoManager

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class DigitalOceanRegionsOperator(BaseOperator):
    """Operator retrieving DigitalOcean regions.

    :return: List of regions
    """

    type = 'digitalocean_regions'

    def __init__(self, *args, **kwargs):  # noqa
        super(DigitalOceanRegionsOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        api_key = os.getenv('DIGITALOCEAN_TOKEN')
        client = DoManager(None, api_key, 2)

        regions = [region["slug"] for region in client.all_regions()]

        return regions


class DigitalOceanInstanceTypesOperator(BaseOperator):
    """
    Operator retrieving the available instance types in a region.

    :param region: [Required] The region to determine the instances in
    :param instance_families: A list of instance families, ie ['g', 'm']
    :return: A list of instance types
    """

    type = 'digitalocean_instance_types'

    def __init__(self, *args, **kwargs):  # noqa
        super(DigitalOceanInstanceTypesOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        selected_region = self.operator_dict['region']
        api_key = os.getenv('DIGITALOCEAN_TOKEN')
        client = DoManager(None, api_key, 2)

        if 'instance_families' not in self.operator_dict:
            instances = [
                item["slug"]
                for item in client.sizes()
                if selected_region in item["regions"]
            ]
        else:
            selected_family = self.operator_dict['instance_families']

            instances = [
                instance
                for instance in [
                    item["slug"].split("-", 1)
                    for item in client.sizes()
                    if selected_region in item["regions"]
                ]
                if len(instance) > 1
                if instance[0] in selected_family
            ]

        instances.sort()

        instances = ['-'.join([s[0], s[1]]) for s in instances]

        return instances
