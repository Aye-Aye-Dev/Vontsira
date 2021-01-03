'''
Created on 28 Dec 2020

@author: si
'''
import json
import random

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from vontsira.controllers.document_storage import document_storage_factory
from vontsira.models import Dataset, DatasetVersion
from vontsira.utils import JsonException


class DatasetController:
    """
    Co-ordinate CRUD for a dataset.

    Each dataset-
    * has a namespaced reference
    * has one or more documents in document-storage
    * has database entries to simplify access to the document store but the document store is the
      primary book so contains all db info plus more.
    """

    def __init__(self, db, document_storage_uri):
        """
        Args:
            db (sqlalchemy)
            document_storage_uri (str) starting file:// or s3:// (not yet implemented) etc. to
                        base of documents
        """
        self.db = db
        self.document_storage = document_storage_factory(document_storage_uri)

        # lazy eval variables
        self._meta_data = None
        self._dataset_record = None
        self._dataset_version_record = None

        # constants
        # top level fields in JSON doc. are cached by DB model
        self.doc_db_fields = ['title']

    @property
    def meta_data(self):
        """
        Returns:
            (dict)
        """
        return self._meta_data

    @property
    def dataset_ref(self):
        """
        Returns:
            (str)
        """
        return self._meta_data['dataset_ref']

    @property
    def version_ref(self):
        """
        Returns:
            (str)
        """
        return self._meta_data['version_ref']

    @property
    def raw_document(self):
        """
        Returns:
            (str)
        """
        return self.document_storage.raw_document

    @property
    def database_record(self):
        """
        Returns:
            (SqlAlchemy ORM record)
        """
        return self._dataset_record

    def load(self, dataset_ref, version_ref=None):
        """
        Args:
            dataset_ref (str)
            version_ref (str) if not given find latest version

        Returns:
            None

        Raises:
            :class:`JsonException` if there are any problems
        """
        if version_ref is not None:

            try:
                self._dataset_record, self._dataset_version_record = self.db.session\
                    .query(Dataset, DatasetVersion)\
                    .filter(Dataset.dataset_ref == dataset_ref)\
                    .filter(Dataset.id == DatasetVersion.dataset_id)\
                    .filter(DatasetVersion.version_ref == version_ref)\
                    .one()

            except (NoResultFound, MultipleResultsFound):
                raise JsonException("Not found", status_code=404)

        else:
            # load latest version
            try:
                r = self.db.session\
                    .query(Dataset, DatasetVersion)\
                    .filter(Dataset.dataset_ref == dataset_ref)\
                    .filter(Dataset.id == DatasetVersion.dataset_id)\
                    .order_by(DatasetVersion.last_updated.desc())\
                    .first()

            except (NoResultFound, MultipleResultsFound):
                r = None

            if r is None:
                raise JsonException("Not found", status_code=404)

        self._dataset_record, self._dataset_version_record = r
        self.document_storage.load(dataset_ref, self._dataset_version_record.version_ref)
        self._meta_data = self.document_storage.meta_data

    @classmethod
    def create_identifier(cls):
        """
        Returns:
            (str)
        """
        ref_permitted_alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        ref = "".join([random.choice(ref_permitted_alphabet) for _ in range(7)])
        return ref

    def _parse_dataset_doc(self, raw_doc):
        """
        Args:
            raw_doc (str) valid JSON document describing the dataset.

        Returns:
            (dict) loaded doc.

        Raises `JsonException` is there are any problems.
        """
        # Ensure it's a valid JSON doc.
        try:
            doc = json.loads(raw_doc)
        except:
            # very broad exception becuase any kind of fail means doc. not reachable or invalid
            # MAYBE TODO - could give a more detailed reason
            raise JsonException("Invalid JSON.", status_code=400)

        if not isinstance(doc, dict):
            raise JsonException("The dataset document must be a dictionary.", status_code=400)

        return doc

    def create_new(self, raw_doc):
        """
        Find an unused dataset_ref; create db entry; create document with metadata first line in
        document_storage
        Args:
            raw_doc (str) valid JSON document describing the dataset.

        Returns:
            None
        """

        # store in document store
        # .. along with metadata in the first line.
        doc = self._parse_dataset_doc(raw_doc)
        dataset_ref = self.create_identifier()
        version_ref = self.create_identifier()
        self._meta_data = {'dataset_ref': dataset_ref,
                           'version_ref': version_ref,
                           }

        # DB is just a cache of a subset of values
        db_record = {'dataset_ref': dataset_ref,
                     }

        for copy_field in self.doc_db_fields:
            db_record[copy_field] = doc.get(copy_field, None)

        # TODO maybe retry on existing dataset ref?
        # Uniqueness pf dataset ref is trusted to the db
        d = Dataset(**db_record)
        self.db.session.add(d)
        dv = DatasetVersion(**{'version_ref': version_ref, 'dataset': d})
        self.db.session.add(dv)
        self.db.session.commit()

        self._dataset_record = d
        self._dataset_version_record = dv
        self.document_storage.write(dataset_ref, version_ref, raw_doc, self._meta_data)
        return

    def update(self, raw_doc, dataset_ref=None):
        """
        Create a new version of the dataset.

        Args:
            dataset_ref (str) Optional but if not supplied :method:`load` must have already been
                        called so the dataset to update will have been chosen

            raw_doc (str) valid JSON document describing the dataset.

        Returns:
            None

        Raises JsonException
        """
        if dataset_ref:
            self.load(dataset_ref)

        if self._meta_data is None:
            raise ValueError("Attempt to attach version without specifying dataset_ref.")

        doc = self._parse_dataset_doc(raw_doc)
        version_ref = self.create_identifier()  # new version ref

        # reset meta data
        self._meta_data = {'dataset_ref': self.dataset_ref,
                           'version_ref': version_ref,
                           }

        # update db :class:`Dataset` record with fields from new doc.
        for copy_field in self.doc_db_fields:
            setattr(self._dataset_record, copy_field, doc.get(copy_field, None))

        dv_r = {'version_ref': version_ref, 'dataset': self._dataset_record}
        self._dataset_version_record = DatasetVersion(**dv_r)
        self.db.session.add(self._dataset_version_record)
        self.db.session.commit()

        self.document_storage.write(self.dataset_ref, version_ref, raw_doc, self._meta_data)
        return
