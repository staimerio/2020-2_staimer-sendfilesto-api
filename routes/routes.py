"""Routes for the app"""

# Retic
from retic import Router
from retic.lib.hooks.middlewares import cors

# Controllers
import controllers.files as files
import controllers.folders as folders
import controllers.photos as photos
import controllers.photos_folder as photos_folder
import controllers.files_folder as files_folder

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
    .get("/files", files.get_latest)

router \
    .post("/files/remote-upload", files.upload_remote) \
    .get("/files/:id", files.get_by_id)

router \
    .post("/files/folder", files_folder.upload_folder)
router \
    .get("/files/folder/:folder/:code/:filename", files_folder.show_by_code)

# Photos routes
router \
    .post("/photos", photos.upload)
router \
    .get("/photos/:album/:filename", photos.show_by_filename)


router \
    .post("/photos/folder", photos_folder.upload_folder)
router \
    .get("/photos/folder/:album/:code/:filename", photos_folder.show_by_code)

# Folder routes
router \
    .get("/folders/:folder", folders.get_by_folder) \
    .delete("/folders/:folder", folders.delete_by_folder)

# Download routes
router \
    .get("/downloads/files/:file", files.download_by_id)
