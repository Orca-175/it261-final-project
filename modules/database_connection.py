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

    def addProduct(self, product):
        with self.db.cursor() as cursor: 
            # Insert product details.
            cursor.execute('INSERT INTO products (name, price, stock, release_date, description)' \
                'VALUES (%s, %s, %s, %s, %s)', 
                (product.name, product.price, product.stock, product.releaseDate, product.description)
            )

            # Get id of inserted product.
            cursor.execute('SELECT id FROM products ORDER BY id DESC')
            id = cursor.fetchone()['id']

            # Store images in id/. TODO: Add filetype verification. Only images are allowed!
            for image in product.images:
                imagePath = self.imageStorageHandler.storeFIleAtId(id, image)
                cursor.execute('INSERT INTO images (product_id, image_path) VALUES(%s, %s)', (id, imagePath))

            # Insert tags to tags table.
            for tag in product.tags:
                cursor.execute('INSERT INTO tags (product_id, tag) VALUES(%s, %s)', (id, tag))


    def getProductListings(self, searchQuery='%'): # Return product info relevant for listings.
        productsArray = []
        with self.db.cursor() as cursor:
            cursor.execute('SELECT products.id, products.name, products.price, products.stock, '
                '(SELECT images.image_path FROM images WHERE images.product_id = products.id LIMIT 1) AS image ' \
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

    def getProductDetails(self, productId): # Return product info of a single product.
        productsDict = {
            'details': {},
            'images': [],
            'tags': [],
        }

        with self.db.cursor() as cursor:
            cursor.execute('SELECT * FROM products WHERE id = %s', (productId))

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
            cursor.execute('UPDATE products SET name = %s, price = %s, stock = %s, release_date = %s, ' \
                'description = %s WHERE id = %s', 
                (product.name, product.price, product.stock, product.releaseDate, product.description, productId)
            )

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
                raise ValueError
