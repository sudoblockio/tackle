# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import boto3

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class AwsAzsOperator(BaseOperator):
    """Operator for retrieving the availability zones in a given region."""

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
        client = boto3.client('ec2')

        availability_zones = [
            zone['ZoneName']
            for zone in client.describe_availability_zones(
                Filters=[
                    {'Name': 'region-name', 'Values': [self.operator_dict['region']]},
                    {'Name': 'state', 'Values': ['available']},
                ]
            )['AvailabilityZones']
        ]
        return availability_zones


class AwsEc2TypesOperator(BaseOperator):
    """Operator retrieving the available instance types in a region."""

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
        client = boto3.client('ec2')

        selected_region = self.operator_dict['region']

        instances = [
            instance['InstanceType']
            for instance in client.describe_instance_type_offerings(
                LocationType='region',
                Filters=[{'Name': 'location', 'Values': [selected_region]}],
            )['InstanceTypeOfferings']
        ]

        if 'instance_families' not in self.operator_dict:
            return instances
        else:
            split_instances = list(
                set([instance.split(".")[0] for instance in instances])
            )
            split_instances.sort()

            # selected_family = ['a1', 'c1']
            selected_family = self.operator_dict['instance_families']
            selected_family = [name + '*' for name in selected_family]

            instances = [
                instance['InstanceType']
                for instance in client.describe_instance_type_offerings(
                    Filters=[{'Name': 'instance-type', 'Values': selected_family}]
                )['InstanceTypeOfferings']
            ]

            return instances


class AwsRegionsOperator(BaseOperator):
    """Operator for printing an input and returning the output."""

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
