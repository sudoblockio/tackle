# -*- coding: utf-8 -*-

"""DigitalOcean hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
from dopy.manager import DoManager
from typing import List

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class DigitalOceanRegionsHook(BaseHook):
    """Hook retrieving DigitalOcean regions.

    :return: List of regions
    """

    type: str = 'digitalocean_regions'
    # region: str

    def execute(self):
        api_key = os.getenv('DIGITALOCEAN_TOKEN')
        client = DoManager(None, api_key, 2)

        regions = [region["slug"] for region in client.all_regions()]

        return regions


class DigitalOceanInstanceTypesHook(BaseHook):
    """Hook retrieving the available instance types in a region.

    :param region: [Required] The region to determine the instances in
    :param instance_families: A list of instance families, ie ['g', 'm']
    :return: A list of instance types
    """

    type: str = 'digitalocean_instance_types'
    region: str
    instance_families: List = None

    def execute(self):
        selected_region = self.region
        api_key = os.getenv('DIGITALOCEAN_TOKEN')
        client = DoManager(None, api_key, 2)

        if not self.instance_families:
            instances = [
                item["slug"]
                for item in client.sizes()
                if selected_region in item["regions"]
            ]
        else:
            selected_family = self.instance_families

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
