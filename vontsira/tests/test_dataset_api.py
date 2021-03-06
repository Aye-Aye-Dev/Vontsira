import json
import os

from vontsira.database import db
from vontsira.models import Dataset
from vontsira.tests.base import BaseTest


class TestDatasetApi(BaseTest):
    """
    Flask API tests for the dataset blueprint.
    """

    def setUp(self):
        super().setUp()

        # don't use relative paths as no guarantee of working directory when running tests
        current_path = os.path.dirname(__file__)
        self.test_data_dir = os.path.abspath(os.path.join(current_path, "data"))

    def get_sample_data(self, sample_name):
        """
        Load sample JSON data and return as a string. i.e. don't de-serialise.

        Args:
            sample_name (str) use file ./data/sample_{sample_name}.json

        Returns (str)
        """
        with open(os.path.join(self.test_data_dir, f'sample_{sample_name}.json')) as f:
            d = f.read()
        return d

    def test_create_then_retrieve_dataset_doc(self):

        r = self.get_sample_data('simple_doc')
        rv = self.test_client.post('/api/dataset/',
                                   data=r,
                                   content_type='application/json'
                                   )
        self.assertEqual(201, rv.status_code)
        meta_data = json.loads(rv.data)

        self.assertIn("dataset_ref", meta_data)
        dataset_ref = meta_data['dataset_ref']
        rv = self.test_client.get(f'/api/dataset/{dataset_ref}')
        self.assertEqual(200, rv.status_code)
        sample_data = json.loads(rv.data)
        self.assertEqual("Orb Spiders", sample_data['title'])

    def test_invalid_json(self):

        r = self.get_sample_data('invalid_json')
        rv = self.test_client.post('/api/dataset/',
                                   data=r,
                                   content_type='application/json'
                                   )
        self.assertEqual(400, rv.status_code)
        self.assertIn('Invalid JSON', rv.data.decode('utf-8'))

    def test_unknown_doc(self):
        rv = self.test_client.get('/api/dataset/aaaaa')
        self.assertEqual(404, rv.status_code)

    def test_doc_fields_to_db(self):

        r = self.get_sample_data('simple_doc')
        rv = self.test_client.post('/api/dataset/',
                                   data=r,
                                   content_type='application/json'
                                   )
        self.assertEqual(201, rv.status_code)
        meta_data = json.loads(rv.data)
        dataset_ref = meta_data['dataset_ref']

        db_recs = db.session.query(Dataset).all()
        self.assertEqual(1, len(db_recs))
        r = db_recs[0]
        self.assertEqual(dataset_ref, r.dataset_ref)
        self.assertEqual('Orb Spiders', r.title)
