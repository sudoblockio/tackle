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


class GcpAzsOperator(BaseOperator):
    """
    Operator for retrieving the availability zones in a given region.

    :param region: A region to search in
    :param regions: A list of regions to search in
    :return: A list of availability zones
    """

    type = 'gcp_azs'

    def __init__(self, *args, **kwargs):  # noqa
        super(GcpAzsOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        client = build('compute', 'v1')

        if 'region' in self.operator_dict:
            azs = self._call_azs(
                client, self.operator_dict['region'], self.operator_dict['gcp_project']
            )
            azs.sort()
            return azs

        elif 'regions' in self.operator_dict:
            output = {}
            for r in self.operator_dict['regions']:
                azs = self._call_azs(client, r, self.operator_dict['gcp_project'])
                azs.sort()
                output.update({r: azs})
            return output

    @staticmethod
    def _call_azs(client, region, project):
        region_uri_stub = (
            "\"https://www.googleapis.com/compute/v1/projects/" + project + "/regions/"
        )
        availability_zones = [
            item['name']
            for item in client.zones()
            .list(
                project=project,
                filter="region=" + region_uri_stub + region + "\" AND status=\"UP\"",
            )
            .execute()['items']
        ]
        availability_zones.sort()
        return availability_zones


class GcpInstanceTypesOperator(BaseOperator):
    """
    Operator retrieving the available instance types in a zone.

    :param region: [Required] The zone to determine the instances in
    :param instance_families: A list of instance families, ie ['n1', 'e2']
    :return: A list of instance types
    """

    type = 'gcp_instance_types'

    def __init__(self, *args, **kwargs):  # noqa
        super(GcpInstanceTypesOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        client = build('compute', 'v1')

        if 'instance_families' not in self.operator_dict:
            instances = [
                item['name']
                for item in client.machineTypes()
                .list(
                    project=self.operator_dict['gcp_project'],
                    zone=self.operator_dict['zone'],
                )
                .execute()['items']
            ]

        else:
            selected_family = self.operator_dict['instance_families']
            selected_family = [name + '-*' for name in selected_family]

            for i, name in enumerate(selected_family):
                if i == 0:
                    query = "name = \"" + name + "\""
                else:
                    query += " OR name = \"" + name + "\""

            instances = [
                item['name']
                for item in client.machineTypes()
                .list(
                    project=self.operator_dict['gcp_project'],
                    zone=self.operator_dict['zone'],
                    filter=query,
                )
                .execute()['items']
            ]

        instances.sort()

        instance_sizes = [
            'micro',
            'small',
            'medium',
            'standard',
            'highcpu',
            'highmem',
            'megamem',
            'ultramem',
        ]

        instance_sizes_set = []
        for _, x in enumerate(instances):
            if len(x.split('-')) == 2:
                instance_sizes_set.append(
                    (
                        x.split('-')[0],
                        x.split('-')[1],
                        None,
                        instance_sizes.index(x.split('-')[1]),
                    )
                )
            else:
                instance_sizes_set.append(
                    (
                        x.split('-')[0],
                        x.split('-')[1],
                        x.split('-')[2],
                        instance_sizes.index(x.split('-')[1]),
                    )
                )

        instance_sizes_set.sort(key=lambda x: x[3])

        instances = []
        for s in instance_sizes_set:
            if s[2]:
                instances.append('-'.join([s[0], s[1], s[2]]))
            else:
                instances.append('-'.join([s[0], s[1]]))

        return instances
