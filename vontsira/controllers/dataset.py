'''
Created on 28 Dec 2020

@author: si
'''
import json
import random

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from vontsira.controllers.document_storage import document_storage_factory
from vontsira.models import Dataset
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

    def create_new(self, raw_doc):
        """
        Find an unused dataset_ref; create db entry; create document with metadata first line in
        document_storage
        Args:
            raw_doc (str) valid JSON document describing the dataset.

        Returns:
            None
        """
        ref_permitted_alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        dataset_ref = "".join([random.choice(ref_permitted_alphabet) for _ in range(7)])

        # store in document store
        # .. along with metadata in the first line.
        # doc can be used for any checks to data. Loading it is also used to ensure it's a valid
        # JSON doc.
        try:
            doc = json.loads(raw_doc)
        except:
            # very broad exception becuase any kind of fail means doc. not reachable or invalid
            # MAYBE TODO - could give a more detailed reason
            raise JsonException("Invalid JSON.", status_code=400)

        if not isinstance(doc, dict):
            raise JsonException("The dataset document must be a dictionary.", status_code=400)

        self._meta_data = {'dataset_ref': dataset_ref,
                           }

        # DB is just a cache of a subset of values
        db_record = {'dataset_ref': dataset_ref,
                     }

        if 'title' in doc:
            db_record['title'] = doc['title']

        # TODO maybe retry on existing dataset ref?
        # Uniqueness pf dataset ref is trusted to the db
        self.db.session.add(Dataset(**db_record))
        self.db.session.commit()

        self.document_storage.write(dataset_ref, raw_doc, self._meta_data)

        return

    def load(self, dataset_ref):
        """
        Args:
            dataset_ref (str)

        Returns:
            None

        Raises:
            :class:`JsonException` if there are any problems
        """
        try:
            self._dataset_record = self.db.session\
                .query(Dataset)\
                .filter(Dataset.dataset_ref == dataset_ref)\
                .one()

        except (NoResultFound, MultipleResultsFound):
            raise JsonException("Not found", status_code=404)

        self.document_storage.load(dataset_ref)
        self._meta_data = self.document_storage.meta_data
