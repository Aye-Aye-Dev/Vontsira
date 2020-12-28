'''
Created on 23 Dec 2020

@author: si
'''
from flask import Flask

from vontsira.database import db
from vontsira.utils import JsonException, handle_json_exception, handle_user_exception,\
    UserException


def create_app(settings_class):
    """
    :param settings_class (str or class) to Flask settings
    """
    # internal import to make it possible to mock.patch
    from vontsira.views.dataset import dataset_view

    app = Flask(__name__)
    app.config.from_object(settings_class)
    db.init_app(app)

    app.register_error_handler(JsonException, handle_json_exception)
    app.register_error_handler(500, handle_json_exception)
    app.register_error_handler(UserException, handle_user_exception)
    app.register_blueprint(dataset_view, url_prefix='/dataset')

    @app.route('/', methods=['GET'])
    def app_root():
        return "Vontsira - a data registry"

    return app
