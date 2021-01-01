'''
Created on 1 Jan 2021

@author: si
'''
from flask import Blueprint, render_template

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
    return "single"
