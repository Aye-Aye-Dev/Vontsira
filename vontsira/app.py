'''
Created on 23 Dec 2020

@author: si
'''
from flask import Flask, render_template

from vontsira.database import db
from vontsira.utils import JsonException, handle_json_exception, handle_user_exception,\
    UserException


def create_app(settings_class):
    """
    :param settings_class (str or class) to Flask settings
    """
    # internal import to make it possible to mock.patch
    from vontsira.views.dataset_api import dataset_api_view
    from vontsira.views.dataset_ui import dataset_ui_view

    app = Flask(__name__)
    app.config.from_object(settings_class)
    db.init_app(app)

    app.register_error_handler(JsonException, handle_json_exception)
    app.register_error_handler(500, handle_json_exception)
    app.register_error_handler(UserException, handle_user_exception)
    app.register_blueprint(dataset_api_view, url_prefix='/api/dataset')
    app.register_blueprint(dataset_ui_view, url_prefix='/dataset')

    @app.route('/', methods=['GET'])
    def app_root():
        return render_template("index.html")

    return app
