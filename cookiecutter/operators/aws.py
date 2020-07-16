# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import boto3

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class AwsRegionsOperator(BaseOperator):
    """
    Operator for printing an input and returning the output.

    :return List of regions
    """

    type = 'aws_regions'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(AwsRegionsOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Print the statement."""
        client = boto3.client('ec2')

        regions = [
            region['RegionName'] for region in client.describe_regions()['Regions']
        ]
        return regions


class AwsAzsOperator(BaseOperator):
    """
    Operator for retrieving the availability zones in a given region.

    :param region: A region to search in
    :param regions: A list of regions to search in
    :return A list of availability zones
    """

    type = 'aws_azs'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(AwsAzsOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Print the statement."""
        if 'region' in self.operator_dict:
            client = boto3.client('ec2', region_name=self.operator_dict['region'])
            azs = self._call_azs(client, self.operator_dict['region'])
            return azs

        elif 'regions' in self.operator_dict:
            output = {}
            for r in self.operator_dict['regions']:
                client = boto3.client('ec2', region_name=r)
                azs = self._call_azs(client, r)
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
        return availability_zones


class AwsEc2TypesOperator(BaseOperator):
    """
    Operator retrieving the available instance types in a region.

    :param region: [Required] The region to determine the instances in
    :param instance_families: A list of instance families, ie ['c5', 'm5']
    :return A list of instance types
    """

    type = 'aws_ec2_types'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(AwsEc2TypesOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Print the statement."""
        selected_region = self.operator_dict['region']
        client = boto3.client('ec2', region_name=selected_region)

        instances = [
            instance['InstanceType']
            for instance in client.describe_instance_type_offerings(
                LocationType='region',
                Filters=[{'Name': 'location', 'Values': [selected_region]}],
            )['InstanceTypeOfferings']
        ]

        if 'instance_families' not in self.operator_dict:
            instances.sort()
            return instances
        else:
            split_instances = list(
                set([instance.split(".")[0] for instance in instances])
            )
            split_instances.sort()

            selected_family = self.operator_dict['instance_families']
            selected_family = [name + '*' for name in selected_family]

            instances = [
                instance['InstanceType']
                for instance in client.describe_instance_type_offerings(
                    Filters=[{'Name': 'instance-type', 'Values': selected_family}]
                )['InstanceTypeOfferings']
            ]
            instances.sort()
            return instances
