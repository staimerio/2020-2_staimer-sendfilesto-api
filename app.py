"""Main app"""

# Retic
from retic import App as app

# Routes
from routes.routes import router

# Add routes to app
app.use(router)

# Crear el servidor
app.listen(
    use_reloader=True,
    use_debugger=True,
    port=1801,
    hostname="localhost"
)