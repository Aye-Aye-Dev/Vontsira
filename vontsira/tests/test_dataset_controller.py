'''
Created on 2 Jan 2021

@author: si
'''
from flask import current_app

from vontsira.controllers.dataset import DatasetController
from vontsira.database import db
from vontsira.models import Dataset, DatasetVersion
from vontsira.tests.base import BaseTest


class TestDatasetController(BaseTest):
    """
    These could be completely seprated from Flask but for now it's easy with create_db which
    needs the app's context.
    """

    def test_new_and_load(self):
        """
        Create and then load a simple document. Should get the latest version but that's not
        checked here.
        """

        dc_a = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
        dc_a.create_new(b'{"title": "Arachnids of Kent"}')

        dc_b = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
        dc_b.load(dc_a.dataset_ref)

        self.assertEqual(dc_a.dataset_ref, dc_b.dataset_ref)

    def test_multiple_versions(self):

        dc_a = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
        dc_a.create_new(b'{"title": "Doc. A"}')
        dc_a.update(b'{"title": "Doc. B"}')
        dc_a.update(b'{"title": "Doc. C"}')
        dc_a.update(b'{"title": "Doc. D"}')

        q = db.session.query(DatasetVersion).order_by(DatasetVersion.last_updated.asc())
        ordered_versions = [(r.version_ref, r.last_updated) for r in q.all()]

        self.assertEqual(4, len(ordered_versions), "There should be 4 versions")

        # This unit test should be using sqlite which uses a very fine grained clock for the last
        # updated field. Ensure these datestamps are all different
        date_stamps = set([str(r[1]) for r in ordered_versions])
        self.assertEqual(4, len(date_stamps), "DB timestamps aren't fine grained enough for test")

        dc_b = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
        dc_b.load(dc_a.dataset_ref)
        latest_version = ordered_versions[-1]
        self.assertEqual(latest_version[0], dc_b.version_ref)
