import json
import os

from vontsira.tests.base import BaseTest


class TestDataset(BaseTest):
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
        rv = self.test_client.post('/dataset/',
                                   data=r,
                                   content_type='application/json'
                                   )
        self.assertEqual(201, rv.status_code)
        meta_data = json.loads(rv.data)

        self.assertIn("dataset_ref", meta_data)
        dataset_ref = meta_data['dataset_ref']
        rv = self.test_client.get(f'/dataset/{dataset_ref}')
        self.assertEqual(200, rv.status_code)
        sample_data = json.loads(rv.data)
        self.assertEqual("Orb Spiders", sample_data['title'])

    def test_invalid_json(self):

        r = self.get_sample_data('invalid_json')
        rv = self.test_client.post('/dataset/',
                                   data=r,
                                   content_type='application/json'
                                   )
        self.assertEqual(400, rv.status_code)
        self.assertIn('Failed to decode JSON object', rv.data.decode('utf-8'))
