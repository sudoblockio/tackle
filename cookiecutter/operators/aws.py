# -*- coding: utf-8 -*-

"""AWS Operators."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import boto3

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class AwsRegionsOperator(BaseOperator):
    """Operator retrieving AWS regions.

    :return: List of regions
    """

    type = 'aws_regions'

    def __init__(self, *args, **kwargs):  # noqa
        super(AwsRegionsOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        client = boto3.client('ec2', region_name='us-east-1')

        regions = [
            region['RegionName'] for region in client.describe_regions()['Regions']
        ]
        return regions


class AwsAzsOperator(BaseOperator):
    """
    Operator for retrieving the availability zones in a given region.

    :param region: A region to search in
    :param regions: A list of regions to search in
    :return: A list of availability zones
    """

    type = 'aws_azs'

    def __init__(self, *args, **kwargs):  # noqa
        super(AwsAzsOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        if 'region' in self.operator_dict:
            client = boto3.client('ec2', region_name=self.operator_dict['region'])
            azs = self._call_azs(client, self.operator_dict['region'])
            azs.sort()
            return azs

        elif 'regions' in self.operator_dict:
            output = {}
            for r in self.operator_dict['regions']:
                client = boto3.client('ec2', region_name=r)
                azs = self._call_azs(client, r)
                azs.sort()
                output.update({r: azs})
            return output

    @staticmethod
    def _call_azs(client, region):
        availability_zones = [
            zone['ZoneName']
            for zone in client.describe_availability_zones(
                Filters=[
                    {'Name': 'region-name', 'Values': [region]},
                    {'Name': 'state', 'Values': ['available']},
                ]
            )['AvailabilityZones']
        ]
        availability_zones.sort()
        return availability_zones


class AwsEc2TypesOperator(BaseOperator):
    """
    Operator retrieving the available instance types in a region.

    :param region: [Required] The region to determine the instances in
    :param instance_families: A list of instance families, ie ['c5', 'm5']
    :return: A list of instance types
    """

    type = 'aws_ec2_types'

    def __init__(self, *args, **kwargs):  # noqa
        super(AwsEc2TypesOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        selected_region = self.operator_dict['region']
        client = boto3.client('ec2', region_name=selected_region)

        if 'instance_families' not in self.operator_dict:
            instances = [
                instance['InstanceType']
                for instance in client.describe_instance_type_offerings(
                    LocationType='region',
                    Filters=[{'Name': 'location', 'Values': [selected_region]}],
                )['InstanceTypeOfferings']
            ]
        else:
            selected_family = self.operator_dict['instance_families']
            selected_family = [name + '*' for name in selected_family]

            instances = [
                instance['InstanceType']
                for instance in client.describe_instance_type_offerings(
                    Filters=[{'Name': 'instance-type', 'Values': selected_family}]
                )['InstanceTypeOfferings']
            ]

        instances.sort()

        instance_sizes = [
            'nano',
            'micro',
            'small',
            'medium',
            'large',
            'xlarge',
            '2xlarge',
            '3xlarge',
            '4xlarge',
            '6xlarge',
            '8xlarge',
            '9xlarge',
            '10xlarge',
            '12xlarge',
            '16xlarge',
            '18xlarge',
            '20xlarge',
            '20xlarge',
            '24xlarge',
            '32xlarge',
            'metal',
        ]

        instance_sizes_set = [
            (x.split('.')[0], x.split('.')[1], instance_sizes.index(x.split('.')[1]))
            for i, x in enumerate(instances)
        ]
        instance_sizes_set.sort(key=lambda x: x[2])
        instances = ['.'.join([s[0], s[1]]) for s in instance_sizes_set]

        return instances
