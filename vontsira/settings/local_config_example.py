import os

from vontsira.settings.global_config import BaseConfig

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config(BaseConfig):
    DB_FILE = os.path.join(PROJECT_DIR, 'vontsira.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE}"
