# Retic
from retic import env, App as app

# PIL
from PIL import Image
# Importing the StringIO module.
from io import BytesIO


# Utils
from services.utils.general import rmfile

# Constants
PUBLIC_IMAGES_FOLDER = app.config.get('PUBLIC_IMAGES_FOLDER')


def compress_images(images):
    """Compress images from a bytes list"""
    _images = []

    for _image in images:
        _image['filename'] = _image['filename'].replace('.png', '.jpg')
        """Path of the image"""
        _output_image_path = "{0}/{1}".format(
            PUBLIC_IMAGES_FOLDER, _image['filename'])
        _image_ins = Image.open(BytesIO(_image['binary']))
        """Save image"""
        _image_ins.convert('RGB').save(_output_image_path, optimize=True, quality=30)
        """Open image"""
        with open(_output_image_path, "rb") as image_file:
            _images.append({
                **_image,
                'binary': image_file.read(),
            })
        """Delete image"""
        rmfile(_output_image_path)

    return _images
