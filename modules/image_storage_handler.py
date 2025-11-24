from os import makedirs
from werkzeug.utils import secure_filename

class ImageStorageHandler:
    def __init__(self, path):
        self.path = path

    def storeFIleAtId(self, id, image):
        pathAtId = f'{self.path}/{id}'
        makedirs(pathAtId, exist_ok=True)

        if image:
            filename = secure_filename(image.filename)
            print(pathAtId)
            image.save(f'{pathAtId}/{filename}')
            return f'{pathAtId}/{filename}'.replace('static/', '')
