"""Routes for the app"""

# Retic
from retic import Router
from retic.lib.hooks.middlewares import cors

# Controllers
import controllers.files as files
import controllers.folders as folders
import controllers.photos as photos

"""Define the router instance"""
router = Router()

"""Add cors settigns"""
router.use(cors())

"""Define the options methods for all routes"""
router.options("/*", cors())

"""Define all routes - Files"""
# Files routes
router \
    .post("/files", files.upload) \
    .get("/files/:id", files.get_by_id)

# Photos routes
router \
    .post("/photos", photos.upload)
router \
    .get("/photos/:album/:filename", photos.show_by_filename)

# Folder routes
router \
    .get("/folders/:folder", folders.get_by_folder) \
    .delete("/folders/:folder", folders.delete_by_folder)

# Download routes
router \
    .get("/downloads/files/:file", files.download_by_id)
