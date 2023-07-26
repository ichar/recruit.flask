# -*- coding: utf-8 -*-
#https://habr.com/ru/articles/351218/

import logging
from flask import Flask, redirect, url_for, session
#from flask_bootstrap import Bootstrap
from flask_cors import CORS, cross_origin
from flask_login import LoginManager
from flask.cli import FlaskGroup

from flask_sqlalchemy import SQLAlchemy
from flask_log_request_id import RequestID, current_request_id

import click
from flask.cli import with_appcontext

from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from datetime import timedelta

from config import IsTrace, config, DEFAULT_CONFIG, print_to

#from .patches import *


db = SQLAlchemy()

'''
from flask_migrate import Migrate
migrate = Migrate(app, db)
'''

#bootstrap = Bootstrap()

login_manager = LoginManager()
login_manager.login_view = 'login_bp.login'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.session_protection = 'basic' # 'strong'

'''
from flask_babel import Babel
babel = Babel(app)
'''
'''
from flask_wtf.csrf import CSRFProtect
csrf_protect = CSRFProtect(app)
'''

'''
from flask_alchemydumps import AlchemyDumps
alchemydumps = AlchemyDumps(app, db)
'''

'''
from flask_security import SQLAlchemyUserDatastore, Security
from app.auth.models.users import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
'''

def create_app(config_name=DEFAULT_CONFIG):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))
    #config[config_name].init_app(app)

    # app.url_map.strict_slashes = False
    UPLOAD_FOLDER = '/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'json'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
    app.config["JSON_SORT_KEYS"] = False

    #app.register_error_handler(403, forbidden)

    #bootstrap.init_app(app)
    #babel.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    RequestID(app)

    from .auth import login_bp, login
    app.register_blueprint(login_bp, url_prefix='/auth')

    from .main import main_bp, main
    app.register_blueprint(main_bp) #, url_prefix="/main"

    from .dialog.dialog import dialog, dialog_bp
    app.register_blueprint(dialog_bp, url_prefix="/dialog")

    from .group.group import group, group_bp
    app.register_blueprint(group_bp, url_prefix="/group")

    from .blank.blank import blank, blank_bp
    app.register_blueprint(blank_bp, url_prefix="/blank")

    from . import docs
    app.register_blueprint(docs.docs_bp, url_prefix="/docs")

    from .booklet.booklet import booklet, booklet_bp
    app.register_blueprint(booklet_bp, url_prefix="/booklet")

    from .recognition import recognition, recognition_bp
    app.register_blueprint(recognition_bp, url_prefix="/recognition")

    from .psychological_testing.psychological_testing import psychological_testing_bp
    app.register_blueprint(psychological_testing_bp, url_prefix="/pt")

    from .printforms import prForms_bp, printforms
    app.register_blueprint(prForms_bp, url_prefix='/printform')

    from .person import person_bp, person
    app.register_blueprint(person_bp, url_prefix='/person')

    from .users import users_bp, users
    app.register_blueprint(users_bp, url_prefix='/editor')

    from .documents import documents_bp, documents
    app.register_blueprint(documents_bp, url_prefix='/documents')

    from .manage import manage_bp, manage
    app.register_blueprint(manage_bp, url_prefix='/manager')

    from .classifiers import classifiers_bp, classifiers
    app.register_blueprint(classifiers_bp, url_prefix='/classifiers')

    from .maps import maps_bp, maps
    app.register_blueprint(maps_bp, url_prefix='/maps')

    from .statistics import statistics, statistics_bp
    app.register_blueprint(statistics_bp, url_prefix='/statistics')

    from .tests_editor import tests_editor_bp, testseditor
    app.register_blueprint(tests_editor_bp, url_prefix='/testseditor')

    from .data import data_bp, data
    app.register_blueprint(data_bp, url_prefix='/data')

    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .addresses import address_bp, addresses
    app.register_blueprint(address_bp, url_prefix="/addresses")

    from .officials import officials_bp, officials
    app.register_blueprint(officials_bp, url_prefix="/officials")

    from .social_select import social_select_bp, social_select
    app.register_blueprint(social_select_bp, url_prefix="/social_select")

    from .graph_test import graphs_test_bp, graph_test
    app.register_blueprint(graphs_test_bp, url_prefix="/graph_test")


    from .commands import commands_bp
    commands_bp.cli.short_help = 'Database utilities >>> type: flask database --help'
    app.register_blueprint(commands_bp, cli_group="database")

    if IsTrace:
        print_to(None, '--> app init')

    return app
