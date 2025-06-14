# py-cute/pup_study_style/__init__.py
import os
from flask import Flask

DATABASE = 'database.db' # Define it once here, or in a config.py

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24), # Changed from app.secret_key directly
        DATABASE=os.path.join(app.instance_path, DATABASE), # Store DB in instance folder
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database functions with the app
    from . import db
    db.init_app(app) # Register db commands (like init-db)

    # Register Blueprints
    from . import auth_routes
    app.register_blueprint(auth_routes.bp)

    from . import main_routes
    app.register_blueprint(main_routes.bp)
    app.add_url_rule('/', endpoint='index') # If home is at '/', link it to main_routes.home

    from . import profile_routes
    app.register_blueprint(profile_routes.bp)

    from . import contact_routes
    app.register_blueprint(contact_routes.bp)

    from . import admin_routes
    app.register_blueprint(admin_routes.bp)

    return app