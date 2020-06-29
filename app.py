"""Main app"""

# Retic
from retic import App as app

# Routes
from routes.routes import router

# SQLAlchemy
from services.sqlalchemy.sqlalchemy import config_sqlalchemy

# Set environment file path
app.env.read_env('.env')

# Add routes to app
app.use(router)

# Add database to app
app.use(config_sqlalchemy(), "db_sqlalchemy")

# Create the web server
# app.listen(
#     use_reloader=True,
#     use_debugger=True,
#     hostname=app.env('APP_HOSTNAME', "localhost"),
#     port=app.env.int('APP_PORT', 1801),
# )


def application(req, res):
    """Deploying and hosting

    We use the application from the App class, it's use for passenger_wsgi.py
    """
    return app.application(req, res)
