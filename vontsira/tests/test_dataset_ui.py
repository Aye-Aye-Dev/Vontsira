'''
Created on 1 Jan 2021

@author: si
'''
from vontsira.database import db
from vontsira.models import Dataset
from vontsira.tests.base import BaseTest


class TestDatasetUi(BaseTest):
    """
    Flask API tests for the user interface dataset blueprint.
    """

    def setUp(self):
        super().setUp()

    def test_dataset_listing(self):

        db_record = {'dataset_ref': 'abababab',
                     'title': 'Bees of the world'
                     }
        db.session.add(Dataset(**db_record))
        db.session.commit()

        rv = self.test_client.get(f'/dataset/')
        self.assertEqual(200, rv.status_code)
        html_body = str(rv.data)
        self.assertIn('<!doctype html>', html_body)
        self.assertIn('Bees of the world', html_body)
