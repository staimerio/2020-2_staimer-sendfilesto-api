"""Routes for the app"""

# Retic
from retic import Router

# Controllers
import controllers.files as files

"""Define the router instance"""
router = Router()

"""Define all routes - Files"""
router \
    .post("/files", files.upload)