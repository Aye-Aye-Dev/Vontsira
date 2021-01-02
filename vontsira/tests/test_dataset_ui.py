'''
Created on 1 Jan 2021

@author: si
'''
from flask import current_app

from vontsira.controllers.dataset import DatasetController
from vontsira.database import db
from vontsira.tests.base import BaseTest


class TestDatasetUi(BaseTest):
    """
    Flask API tests for the user interface dataset blueprint.
    """

    def setUp(self):
        super().setUp()

    def add_sample_record(self):
        "Add single sample record to DB using the controller"
        dc = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
        dc.create_new(b'{"title": "Bees of the world"}')
        self.dataset_ref = dc.dataset_ref

    def test_dataset_listing(self):
        self.add_sample_record()

        rv = self.test_client.get('/dataset/')
        self.assertEqual(200, rv.status_code)
        html_body = str(rv.data)
        self.assertIn('<!doctype html>', html_body)
        self.assertIn('Bees of the world', html_body)

    def test_dataset_view(self):
        self.add_sample_record()

        rv = self.test_client.get(f'/dataset/{self.dataset_ref}')
        self.assertEqual(200, rv.status_code)
        html_body = str(rv.data)
        self.assertIn('<!doctype html>', html_body)
        self.assertIn('<td>Title</td><td>Bees of the world</td>', html_body)
