from vontsira.tests.base import BaseTest


class TestAppGeneral(BaseTest):

    def test_empty_root(self):
        rv = self.test_client.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("Vontsira", str(rv.data))
