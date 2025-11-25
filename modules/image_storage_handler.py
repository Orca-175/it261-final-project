from os import makedirs
from werkzeug.utils import secure_filename
from shutil import rmtree

class ImageStorageHandler:
    def __init__(self, path):
        self.path = path

    def storeFileAtId(self, id, image):
        pathAtId = f'{self.path}/{id}'
        makedirs(pathAtId, exist_ok=True)

        if image:
            filename = secure_filename(image.filename)
            image.save(f'{pathAtId}/{filename}')
            return f'{pathAtId}/{filename}'.replace('static/', '')

    def deleteDirectoryAtId(self, id):
        rmtree(f'{self.path}/{id}')
