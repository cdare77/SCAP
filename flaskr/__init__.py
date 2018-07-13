import os
import logging
import logging.handlers

from flask import Flask
from flask_bootstrap import Bootstrap

UPLOAD_FOLDER = os.getcwd() + '/flaskr/uploads'

def create_app(test_config=None): 

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # enable Bootstrap
    Bootstrap(app)

    handler = logging.handlers.RotatingFileHandler(
        'app.log',
        maxBytes=1024 * 1024)
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    from . import checks
    app.register_blueprint(checks.bp)

    from . import results
    app.register_blueprint(results.bp)

    return app
