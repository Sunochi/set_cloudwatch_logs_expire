# -*- coding: utf-8 -*-
"""Test module of lambda_function module."""
import json
import tempfile

from mock import Mock
from nose.tools import eq_, ok_
from unittest import TestCase

from src import lambda_function as l

TEST_LOG_GROUPS_1 = {
    'logGroups': [
        {
            'logGroupName': 'test_log_1',
            'retentionInDays': 7,
        },
        {
            'logGroupName': 'test_log_2',
        },
    ],
    'nextToken':
    '1234567890'
}

TEST_LOG_GROUPS_2 = {
    'logGroups': [{
        'logGroupName': 'test_log_3',
        'retentionInDays': 30
    }]
}


class LambdaFunctionTestCase(TestCase):
    """Test class of lambda_function module."""
    def setUp(self):
        """Set up before test methods."""
        self.event = json.load(open('test_event.json', 'r'))
        self.context = None

        l.LOGS_CLIENT = Mock()
        l.LOGS_CLIENT.describe_log_groups.side_effect = [
            TEST_LOG_GROUPS_1, TEST_LOG_GROUPS_2
        ]
        l.LOGS_CLIENT.put_retention_policy.return_value = None

    def tearDown(self):
        """Tear down after test methods."""
        pass

    def test_lambda_handler(self):
        """Test test_lambda_handler(self)."""
        eq_(None, l.lambda_handler(self.event, self.context))

        l.LOGS_CLIENT.describe_log_groups.side_effect = Exception("test")
        eq_(None, l.lambda_handler(self.event, self.context))

        l.LOGS_CLIENT.describe_log_groups.side_effect = l.ClientError(
            {
                'Error': {
                    'Code': 404,
                    'Message': 'NotFound',
                },
            },
            'NotoFound',
        )
        eq_(None, l.lambda_handler(self.event, self.context))

    def test_fetch_log_list(self):
        """Test fetch_log_list()."""
        expected = []
        expected.extend(TEST_LOG_GROUPS_1['logGroups'])
        expected.extend(TEST_LOG_GROUPS_2['logGroups'])
        eq_(expected, l.fetch_log_list())

    def test_generate_set_expire_list(self):
        """Test generate_set_expire_list(log_list)."""
        log_list = []
        log_list.extend(TEST_LOG_GROUPS_1['logGroups'])
        log_list.extend(TEST_LOG_GROUPS_2['logGroups'])
        expected = ['test_log_2']
        eq_(expected, l.generate_set_expire_list(log_list))

    def test_set_expire_to_target_list(self):
        """Test set_expire_to_target_list(target_list)."""
        target_list = ['test_log_1', 'test_log_2']
        expected = None
        eq_(expected, l.set_expire_to_target_list(target_list))

    def test_create_message(self):
        """Test create_message(log_list)."""
        log_list = ['test_log_1', 'test_log_2']
        ok_(l.create_message(log_list))

        log_list = []
        ok_(l.create_message(log_list))
