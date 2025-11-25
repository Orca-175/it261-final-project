import app_factory
from flask_bcrypt import check_password_hash
from modules.exceptions import PasswordLengthError, ProductNotFoundError, UserNotFoundError, UsernameTakenError, WrongPasswordError
from models.user import User
from pymysql import connect, cursors

class DatabaseConnection:
    def __init__(self, host, user, password, database, imageStorageHandler):
        self.db = connect(
            host=host, 
            user=user, 
            password=password, 
            database=database, 
            cursorclass=cursors.DictCursor,
            autocommit=True)
        self.imageStorageHandler = imageStorageHandler


    # For user_loader
    def getCustomer(self, userId):
        with self.db.cursor() as cursor:
            if cursor.execute('SELECT * FROM customers WHERE id = %s', [userId]) < 1:
                return None
            customer = cursor.fetchone()
            return User(customer['id'], customer['username'], customer['approved'], 'customer')


    def getAdmin(self, adminId):
        with self.db.cursor() as cursor:
            if cursor.execute('SELECT * FROM admins WHERE id = %s', [adminId]) < 1:
                return None
            admin = cursor.fetchone()
            return User(admin['id'], admin['username'], admin['approved'], 'admin')


    def registerCustomer(self, username, password):
        with self.db.cursor() as cursor:
            if cursor.execute('SELECT * FROM customers WHERE username = %s', [username]) > 0:
                raise UsernameTakenError(f'Username "{username}" already exists.')
            if len(password) < 8:
                raise PasswordLengthError('Password must be atleast 8 characters long.')

            try: 
                cursor.execute('INSERT INTO customers (username, password) '
                    'VALUES (%s, %s)', [username, app_factory.bcrypt.generate_password_hash(password).decode()])
            except Exception:
                raise Exception


    def registerAdmin(self, username, password):
        with self.db.cursor() as cursor:
            if cursor.execute('SELECT * FROM admins WHERE username = %s', [username]) > 0:
                raise UsernameTakenError(f'Username "{username}" already exists.')
            if len(password) < 8: 
                raise PasswordLengthError('Password must be atleast 8 characters long.')
            
            try:
                cursor.execute('INSERT INTO admins (username, password)'
                    'VALUES (%s, %s)', [username, app_factory.bcrypt.generate_password_hash(password).decode()])
            except Exception:
                raise Exception


    def authenticateCustomer(self, username, password):
        with self.db.cursor() as cursor:
            rowsNumber = cursor.execute('SELECT * FROM customers WHERE username = %s', [username])
            if rowsNumber < 1:
                raise UserNotFoundError
            customer = cursor.fetchone()

            if not check_password_hash(customer['password'], password):
                raise WrongPasswordError
            return User(customer['id'], customer['username'], customer['approved'], 'customer')
    
    def authenticateAdmin(self, username, password):
        with self.db.cursor() as cursor:
            rowsNumber = cursor.execute('SELECT * FROM admins WHERE username = %s', [username])
            if rowsNumber < 1:
                raise UserNotFoundError
            admin = cursor.fetchone()

            if not check_password_hash(admin['password'], password):
                raise WrongPasswordError
            return User(admin['id'], admin['username'], admin['approved'], 'admin')


    def addProduct(self, product):
        with self.db.cursor() as cursor: 
            cursor.execute('INSERT INTO products (name, price, stock, release_date, description)' \
                'VALUES (%s, %s, %s, %s, %s)', 
                (product.name, product.price, product.stock, product.releaseDate, product.description)
            )

            cursor.execute('SELECT id FROM products ORDER BY id DESC')
            id = cursor.fetchone()['id']

            for image in product.images:
                imagePath = self.imageStorageHandler.storeFileAtId(id, image)
                cursor.execute('INSERT INTO images (product_id, image_path) VALUES(%s, %s)', (id, imagePath))

            for tag in product.tags:
                cursor.execute('INSERT INTO tags (product_id, tag) VALUES(%s, %s)', (id, tag.lower()))

    def getProductListings(self, searchQuery='%'): # Return product info relevant for listings.
        productsArray = []
        with self.db.cursor() as cursor:
            cursor.execute('SELECT products.id, products.name, products.price, products.stock, '
                '(SELECT images.image_path FROM images WHERE images.product_id = products.id LIMIT 1) AS image ' 
                'FROM products WHERE products.name LIKE %s ORDER BY products.name',
                (searchQuery)
            )

            for product in cursor.fetchall():
                tags = []
                cursor.execute('SELECT tag FROM tags WHERE product_id = %s LIMIT 2', (product['id']))
                for tag in cursor.fetchall():
                    tags.append(tag['tag'].upper())
                product['tags'] = tags

                productsArray.append(product)

            return productsArray

    def getProductDetails(self, productId): # Return all product info of a single product.
        productsDict = {
            'details': {},
            'images': [],
            'tags': [],
        }

        with self.db.cursor() as cursor:
            if cursor.execute('SELECT * FROM products WHERE id = %s', (productId)) < 1:
                raise ProductNotFoundError(f'Product at ID {productId} was not found.')

            for product in cursor.fetchall():
                productsDict['details'] = product
            
            cursor.execute('SELECT image_path FROM images WHERE product_id = %s', (productId))

            for product in cursor.fetchall():
                productsDict['images'].append(product['image_path'])

            cursor.execute('SELECT tag FROM tags WHERE product_id = %s', (productId))
            for product in cursor.fetchall():
                productsDict['tags'].append(product['tag'].upper())

        return productsDict

    def editProduct(self, productId, product, thumbnailIndex):
        with self.db.cursor() as cursor:
            rowsNumber = cursor.execute('UPDATE products SET name = %s, price = %s, stock = %s, release_date = %s, ' \
                'description = %s WHERE id = %s', 
                (product.name, product.price, product.stock, product.releaseDate, product.description, productId)
            )

            if rowsNumber < 1:
                raise ProductNotFoundError(f'Product at ID {productId} was not found.')

            imageList = []
            cursor.execute('SELECT image_path FROM images WHERE product_id = %s', (productId))
            for image in cursor.fetchall():
                imageList.append(image['image_path'])
            newThumbnail = imageList.pop(thumbnailIndex)
            imageList.insert(0, newThumbnail)

            cursor.execute('DELETE FROM images WHERE product_id = %s', (productId))
            for imagePath in imageList:
                cursor.execute('INSERT INTO images (product_id, image_path) VALUES (%s, %s)', (productId, imagePath))
            
            cursor.execute('DELETE FROM tags WHERE product_id = %s', (productId))
            for tag in product.tags:
                cursor.execute('INSERT INTO tags (product_id, tag) VALUES (%s, %s)', (productId, tag))
            

    def deleteProduct(self, productId):
        with self.db.cursor() as cursor:
            if cursor.execute('DELETE FROM products WHERE id = %s', (productId)) < 1:
                raise ProductNotFoundError(f'Could not delete product "{productId}"')
            self.imageStorageHandler.deleteDirectoryAtId(productId)
