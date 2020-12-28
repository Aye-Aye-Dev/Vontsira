'''
Created on 23 Dec 2020

@author: si
'''
import unittest

import logging
logging.disable(logging.ERROR)

from vontsira.app import create_app
from vontsira.database import create_database
from vontsira.settings.test_config import Config


class BaseTest(unittest.TestCase):

    def setUp(self):

        self.config = Config()
        self.app = create_app(self.config)
        self.show_log_messages = True

        self.test_client = self.app.test_client()
        create_database(self.app)

        self.request_context = self.app.test_request_context()
        self.request_context.push()

    def tearDown(self):
        self.config.clean_up()
        self.request_context.pop()

    def log(self, msg):
        if self.show_log_messages:
            print(msg)
