from . import model


def init_app():
    """Construct the core application."""
    app = server.app

    model.db.init_app(app)

    with app.app_context():
        from . import server  # Import routes
        model.db.create_all()  # Create sql tables for our data models

        return app
