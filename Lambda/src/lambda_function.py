# -*- coding: utf-8 -*-
"""check diff dh global ip"""
from botocore.exceptions import ClientError

import boto3
import json
import logging
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

AWS_REGION = os.getenv('TARGET_AWS_REGION', 'ap-northeast-1')
LOGS_CLIENT = boto3.client('logs', region_name=AWS_REGION)

EXPIRED_DAYS = os.getenv('EXPIRED_DAYS', 30)


def lambda_handler(event, context):
    """Handle lambda events and return a mixed value.
    This function is required. Don't remove this.
    """
    message = "Lambda:set_cloudwatch_expire\n"
    try:
        LOGGER.info({'event': event, 'context': context})

        all_log_list = fetch_log_list()
        target_log_list = generate_set_expire_list(all_log_list)
        set_expire_to_target_list(target_log_list)

        message += create_message(target_log_list)

    except ClientError as e:
        message += 'ClientError happened. Process False!'
        LOGGER.error('Boto3 Error.')
        LOGGER.error(e)

    except Exception as e:
        message += 'Error happened. Process False!'
        LOGGER.error(e)

    LOGGER.info(message)

    return


def fetch_log_list():
    """Fetch CloudWatch Logs list by boto3 API."""
    log_list = []
    resp = LOGS_CLIENT.describe_log_groups()
    log_list.extend(resp['logGroups'])

    while 'nextToken' in resp:
        resp = LOGS_CLIENT.describe_log_groups(nextToken=resp['nextToken'])
        log_list.extend(resp['logGroups'])

    LOGGER.info({'log_list': log_list})
    return log_list


def generate_set_expire_list(log_list):
    """Generate list need seting expire."""
    set_expire_list = []
    for log in log_list:
        if 'retentionInDays' not in log:
            set_expire_list.append(log['logGroupName'])

    LOGGER.info({'set_expire_list': set_expire_list})
    return set_expire_list


def set_expire_to_target_list(target_list):
    """Set expire EXPIRED_DAYS for CloudWatch Logs in target_list."""
    for target_name in target_list:
        LOGS_CLIENT.put_retention_policy(logGroupName=target_name,
                                         retentionInDays=EXPIRED_DAYS)

    return


def create_message(log_list):
    """Create message."""
    message = 'Process Success!\n'
    for log in log_list:
        message += '%s\n' % (log)

    message += '\n'
    message += '`Set these logs retention periods to %s days.`' % (
        EXPIRED_DAYS)

    return message
