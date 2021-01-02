'''
Created on 1 Jan 2021

@author: si
'''
from flask import Blueprint, current_app, render_template

from vontsira.controllers.dataset import DatasetController
from vontsira.database import db
from vontsira.models import Dataset

dataset_ui_view = Blueprint('dataset_ui', __name__)


@dataset_ui_view.route('/')
def list_datasets():
    """
    list datasets - uses DB and not document store
    """
    datasets = db.session\
        .query(Dataset)\
        .order_by(Dataset.last_updated.desc())\
        .all()

    page_vars = {'datasets': datasets,
                 'page_name': 'All Datasets',
                 }
    return render_template("dataset_list.html", **page_vars)


@dataset_ui_view.route('/<dataset_ref>', methods=['GET'])
def single_dataset(dataset_ref):
    """
    Return the original document,
    """
    dc = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
    dc.load(dataset_ref)
    page_vars = {'dataset': dc.database_record,
                 'raw_document': dc.raw_document,
                 'page_name': f'{dc.database_record.title} ({dc.database_record.dataset_ref})',
                 }
    return render_template("dataset_single.html", **page_vars)
