import os
from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    """Application factory to create and configure the Flask app."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, os.pardir))

    app = Flask(
        __name__,
        static_folder=os.path.join(project_root, 'static'),
        template_folder=os.path.join(project_root, 'templates'),
    )

    # Basic config
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['ADMIN_TOKEN'] = os.environ.get('ADMIN_TOKEN', 'changeme')

    # Enable CORS by default
    CORS(app)

    # Initialize shared services
    from .core.storage import ensure_data_dir
    from .core.ai import init_ai_assistant

    ensure_data_dir()
    app.extensions = getattr(app, 'extensions', {})
    app.extensions['ai_assistant'] = init_ai_assistant()

    # Register blueprints
    from .routes.api import api_bp
    from .routes.web import web_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app




