from app import model
from alembic.config import Config
from alembic import command


def init_app():
    """Construct the core application."""
    app = model.app

    model.db.init_app(app)

    with app.app_context():
        from .app import server  # Import routes
        
        # Run database migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        # Keep db.create_all() as a fallback for development
        # model.db.create_all()  # Create sql tables for our data models

        return app
