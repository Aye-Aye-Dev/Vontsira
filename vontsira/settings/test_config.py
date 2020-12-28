import os
import shutil
import tempfile

from vontsira.settings.global_config import BaseConfig


class Config(BaseConfig):
    DEBUG = True
    TESTING = True
    DB_IN_MEMORY = True
    DB_FILE = None  # changed to a temp file before use
    DB_FD = None
    SQLALCHEMY_DATABASE_URI = None  # replaced with instance var in __init__

    def __init__(self):
        if self.DB_IN_MEMORY:
            self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        else:
            self.DB_FD, self.DB_FILE = tempfile.mkstemp()
            self.SQLALCHEMY_DATABASE_URI = "sqlite:///%s" % self.DB_FILE
        #print("using db [%s]" % self.SQLALCHEMY_DATABASE_URI)

        self.DOCUMENT_STORAGE_URI = "file://" + tempfile.mkdtemp()

    def clean_up(self):
        if not self.DB_IN_MEMORY and self.DB_FILE:
            os.close(self.DB_FD)
            # print "deleting %s" % self.DB_FILE
            os.unlink(self.DB_FILE)

        if self.DOCUMENT_STORAGE_URI.startswith('file://'):
            storage_path = self.DOCUMENT_STORAGE_URI[7:]
            #print(f"deleting {storage_path}")
            shutil.rmtree(storage_path)
