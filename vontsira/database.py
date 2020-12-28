'''
Created on 23 Dec 2020

@author: si
'''
import os

from alembic.config import Config
from alembic import command
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError, ProgrammingError

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

db = SQLAlchemy()


def create_database(app):
    import vontsira.models
    with app.app_context():
        db.create_all()

    return app


def migrate_database(app):
    """
    Ensure database schema is up to date.
    """
    PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
    alembic_ini = os.path.join(PROJECT_DIR, "..", "alembic.ini")
    alembic_cfg = Config(alembic_ini)
    sql = "SELECT * FROM alembic_version"
    new_db = False
    with app.app_context():
        try:
            db.engine.execute(sql).fetchall()
        except (OperationalError, ProgrammingError):
            new_db = True

    if new_db:
        # Setup the alembic table and stamp with current revision as the models
        # contain all changes in the alembic versions
        command.stamp(alembic_cfg, 'head')

    else:
        command.upgrade(alembic_cfg, 'head')
