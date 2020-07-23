# -*- coding: utf-8 -*-

"""Azure Operators."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import re

from azure.common.credentials import ServicePrincipalCredentials
import azure.mgmt.compute as compute
import azure.mgmt.subscription as sub

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class AzureRegionsOperator(BaseOperator):
    """Operator retrieving Azure regions.

    :return: List of regions
    """

    type = 'azure_regions'

    def __init__(self, *args, **kwargs):  # noqa
        super(AzureRegionsOperator, self).__init__(*args, **kwargs)

    def _execute(self):
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


class AzureVMTypesOperator(BaseOperator):
    """
    Operator retrieving the available instance types in a region.

    :param region: [Required] The region to determine the instances in
    :param instance_families: A list of instance families, ie ['A', 'D']
    :return: A list of instance types
    """

    type = 'azure_vm_types'

    def __init__(self, *args, **kwargs):  # noqa
        super(AzureVMTypesOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        subscription_id = os.environ['ARM_SUBSCRIPTION_ID']

        credentials = ServicePrincipalCredentials(
            client_id=os.environ['ARM_CLIENT_ID'],
            secret=os.environ['ARM_CLIENT_SECRET'],
            tenant=os.environ['ARM_TENANT_ID'],
        )

        selected_region = self.operator_dict['region']
        client = compute.ComputeManagementClient(credentials, subscription_id)

        if 'instance_families' not in self.operator_dict:
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
            selected_family = self.operator_dict['instance_families']
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
