from flask import Blueprint, current_app, jsonify, make_response, request

from vontsira.controllers.dataset import DatasetController
from vontsira.database import db

dataset_view = Blueprint('dataset_views', __name__)


@dataset_view.route('/')
def home_dashboard():
    """
    list datasets
    """
    raise NotImplementedError("TODO")


@dataset_view.route('/', methods=['POST'])
def dataset_document_new():
    """
    The document is stored in the document-store with 'dataset_ref' as the name of the document.
    Create a new dataset ref.
    """
    dc = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
    dc.create_new(request.get_data())

    response = jsonify(dc.meta_data)
    return response, 201


@dataset_view.route('/<dataset_ref>', methods=['GET'])
def dataset_document_view(dataset_ref):
    """
    Return the original document,
    """
    dc = DatasetController(db, current_app.config['DOCUMENT_STORAGE_URI'])
    dc.load(dataset_ref)
    response = make_response(dc.raw_document)
    # content type was enforced by DatasetController when document was added
    response.headers["Content-type"] = 'application/json'
    return response, 200
