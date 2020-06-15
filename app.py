"""Main app"""

# Retic
from retic import App as app

# Routes
from routes.routes import router

# SQLAlchemy
from services.sqlalchemy.sqlalchemy import config_sqlalchemy

# Add routes to app
app.use(router)

# Add database to app
app.use(config_sqlalchemy(), "db_sqlalchemy")

# Crear el servidor
app.listen(
    use_reloader=True,
    use_debugger=True,
    port=1801,
    hostname="localhost"
)
