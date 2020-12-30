'''
Created on 28 Dec 2020

@author: si
'''
import os

import ndjson


def document_storage_factory(document_storage_uri):
    """
    Returns:
        instantiated concrete subclass of :class:`AbstractDocumentStorage`
    """
    if document_storage_uri.startswith('file://'):
        storage_path = document_storage_uri[7:]
        doc_storage = FilesystemDocumentStorage(filesystem_path=storage_path)
        return doc_storage

    raise NotImplementedError(f"TODO storage type for {document_storage_uri}")


class AbstractDocumentStorage:

    def __init__(self):
        # lazy eval
        self.meta_data = None
        self.raw_document = None

    def load(self, dataset_ref):
        """
        Args:
            dataset_ref (str)
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def write(self, dataset_ref, raw_document, meta_data):
        """
        Args:
            dataset_ref (str)
            raw_document (str) must be utf8
            meta_data (dict) that is safe to encode as JSON
        """
        raise NotImplementedError("Must be implemented by subclasses")


class FilesystemDocumentStorage(AbstractDocumentStorage):
    def __init__(self, filesystem_path):
        super().__init__()
        self.filesystem_path = filesystem_path

    def load(self, dataset_ref):
        document_path = os.path.join(self.filesystem_path, dataset_ref)
        with open(document_path, 'r') as f:
            self.meta_data = f.readline()
            self.raw_document = f.read()

    def write(self, dataset_ref, raw_document, meta_data):

        document_path = os.path.join(self.filesystem_path, dataset_ref)
        with open(document_path, 'w') as f:
            w = ndjson.writer(f)
            w.writerow(meta_data)
            # TODO either use base64 or carefully check for utf8 and fail to user if not
            f.write(raw_document.decode('utf8'))
