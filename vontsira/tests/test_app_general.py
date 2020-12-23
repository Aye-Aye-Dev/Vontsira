import shutil
import tempfile

from vontsira.tests.base import BaseTest


class TestAppGeneral(BaseTest):

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.temp_dir)

    def test_empty_root(self):
        rv = self.test_client.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("Vontsira", str(rv.data))
