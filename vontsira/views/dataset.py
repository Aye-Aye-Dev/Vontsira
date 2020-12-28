import os
import random

from flask import Blueprint, current_app, jsonify, make_response, request
import ndjson

from vontsira.database import db
from vontsira.models import Dataset
from vontsira.utils import get_object_or_404, JsonException

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
    ref_permitted_alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    dataset_ref = "".join([random.choice(ref_permitted_alphabet) for _ in range(7)])

    meta_data = {'dataset_ref': dataset_ref
                 }

    dbr = {'dataset_ref': dataset_ref
           }

    # TODO maybe retry on existing dataset ref?
    # Uniqueness pf dataset ref is trusted to the db
    db.session.add(Dataset(**dbr))
    db.session.commit()

    # store in document store
    # .. along with metadata in the first line.
    # request.json can be used for any checks to data. Using it raises exception when doc. isn't
    # well formed.
    if not isinstance(request.json, dict):
        raise JsonException("The dataset document must be a dictionary.", status_code=400)

    doc_raw = request.get_data()

    document_storage = current_app.config['DOCUMENT_STORAGE_URI']
    if document_storage.startswith('file://'):
        storage_path = document_storage[7:]
    else:
        raise NotImplementedError(f"TODO storage type for {document_storage}")

    document_path = os.path.join(storage_path, dataset_ref)
    with open(document_path, 'w') as f:
        w = ndjson.writer(f)
        w.writerow(meta_data)
        # TODO either use base64 or carefully check for utf8 and fail to user if not
        f.write(doc_raw.decode('utf8'))

    response = jsonify(meta_data)
    return response, 201


@dataset_view.route('/<dataset_ref>', methods=['GET'])
def dataset_document_view(dataset_ref):
    """
    """
    dataset = get_object_or_404(Dataset, Dataset.dataset_ref == dataset_ref)

    document_storage = current_app.config['DOCUMENT_STORAGE_URI']
    if document_storage.startswith('file://'):
        storage_path = document_storage[7:]
    else:
        raise NotImplementedError(f"TODO storage type for {document_storage}")

    document_path = os.path.join(storage_path, dataset_ref)
    with open(document_path, 'r') as f:
        meta_data = f.readline()
        raw_doc = f.read()

    response = make_response(raw_doc)
    response.headers["Content-type"] = 'application/json'
    return response, 200
