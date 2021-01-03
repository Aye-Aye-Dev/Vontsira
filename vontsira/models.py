'''
Created on 23 Dec 2020

@author: si
'''
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from vontsira.base_model import BaseModel
from vontsira.database import db


# class User(BaseModel, db.Model):
#     __tablename__ = 'user'
#     user_name = Column(String(150), unique=True, nullable=False)
#     password = Column(String(64), nullable=False)
#     active = Column(Boolean)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     tokens = relationship('SessionToken', backref='user')
#
#
# class SessionToken(BaseModel, db.Model):
#     __tablename__ = 'session_token'
#     token_id = Column(String(16), unique=True, nullable=False)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     starts = Column(DateTime, default=datetime.utcnow)
#     expires = Column(DateTime)


class Dataset(BaseModel, db.Model):
    __tablename__ = 'dataset'
    dataset_ref = Column(String(36), nullable=False, index=True, unique=True)
    title = Column(String(255), nullable=True)


class DatasetVersion(BaseModel, db.Model):
    __tablename__ = 'dataset_version'
    version_ref = Column(String(36), nullable=False, index=True)
    dataset_id = Column(Integer, ForeignKey('dataset.id'), nullable=False)
    dataset = relationship("Dataset", backref=backref('versions'))

    table_args = (UniqueConstraint('dataset_id', 'version_ref', name='version_ref_unique'))
