# -*- coding: utf-8 -*-

"""Azure hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import re
from typing import List

from azure.common.credentials import ServicePrincipalCredentials
import azure.mgmt.compute as compute
import azure.mgmt.subscription as sub

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class AzureRegionsHook(BaseHook):
    """Hook retrieving Azure regions.

    :return: List of regions
    """

    type: str = 'azure_regions'

    def execute(self):
        subscription_id = os.environ['ARM_SUBSCRIPTION_ID']

        credentials = ServicePrincipalCredentials(
            client_id=os.environ['ARM_CLIENT_ID'],
            secret=os.environ['ARM_CLIENT_SECRET'],
            tenant=os.environ['ARM_TENANT_ID'],
        )

        client = sub.SubscriptionClient(credentials)

        regions = [
            region.name
            for region in client.subscriptions.list_locations(subscription_id)
        ]
        return regions


class AzureVMTypesHook(BaseHook):
    """
    Hook retrieving the available instance types in a region.

    :param region: [Required] The region to determine the instances in
    :param instance_families: A list of instance families, ie ['A', 'D']
    :return: A list of instance types
    """

    type: str = 'azure_vm_types'
    region: str
    instance_families: List = None

    def execute(self):
        subscription_id = os.environ['ARM_SUBSCRIPTION_ID']

        credentials = ServicePrincipalCredentials(
            client_id=os.environ['ARM_CLIENT_ID'],
            secret=os.environ['ARM_CLIENT_SECRET'],
            tenant=os.environ['ARM_TENANT_ID'],
        )

        selected_region = self.region
        client = compute.ComputeManagementClient(credentials, subscription_id)

        if not self.instance_families:
            instances = list(
                set(
                    [
                        i.name
                        for i in client.resource_skus.list(
                            filter="location eq '" + selected_region + "'"
                        )
                    ]
                )
            )

        else:
            selected_family = self.instance_families
            selected_family = ['^' + name for name in selected_family]

            instances = list(
                set(
                    [
                        i.name
                        for i in client.resource_skus.list(
                            filter="location eq '" + selected_region + "'"
                        )
                    ]
                )
            )

            instances_split = [i.split("_", 1) for i in instances]

            for i, name in enumerate(selected_family):
                if i == 0:
                    exp = name
                else:
                    exp += "|" + name

            exp = re.compile(exp)

            instance_sizes_set = [
                i for i in instances_split if len(i) == 2 if exp.match(i[1])
            ]

            instance_sizes_set.sort(key=lambda x: x[1])

            instances = ['-'.join([s[0], s[1]]) for s in instance_sizes_set]

        return instances
