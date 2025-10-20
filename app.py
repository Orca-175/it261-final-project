from pymysql import connect, cursors
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.db = connect(
            host=host, 
            user=user, 
            password=password, 
            database=database, 
            autocommit=True, 
            cursorclass=cursors.DictCursor)

    def addProduct(self, product):
        with self.db.cursor() as cursor: 
            print('in .addProduct()')
            # Insert product details.
            cursor.execute('INSERT INTO products (name, price, stock, release_date, description) \
                VALUES (%s, %s, %s, %s, %s)', 
                (product.name, product.price, product.stock, product.release_date, product.description))
            print('insert executed')

            # Get id of inserted product.
            cursor.execute('SELECT id FROM products ORDER BY id DESC')
            id = cursor.fetchone()
            print('get id executed')

            # Insert images to images table.
            for image in product.images:
                print('in image loop')
                cursor.execute('INSERT INTO images (product_id, image, mimetype) VALUES(%s, %s, %s)', (id, image[0], image[1]))
            print('insert images executed')

            # Insert tags to tags table.
            for tag in product.tags:
                cursor.execute('INSERT INTO tags (product_id, tag) VALUES(%s, %s)', (id, tag))
            print('insert tags executed')

            cursor.close()

    def getProductListings(self): # Return product info relevant for displaying listings.
        productsArray = []
        with self.db.cursor() as cursor:
            cursor.execute('SELECT id, name, price FROM PRODUCTS')

            for product in cursor.fetchall():
                print(f'product: {product}:{type(product)}')
                # Add product details to dictionary.
                productsArray.append(product) 

            cursor.close()
            return productsArray
    
    def getProductPageInfo(): # Return product info relevant for displaying main product page
        pass

    def getProductThumbnail(self, productId): # Return product image for listing thumbnail
        with self.db.cursor() as cursor:
            cursor.execute('SELECT image, mimetype FROM images WHERE product_id = %s', (productId))
            thumbnail = cursor.fetchone()

            cursor.close()
            return thumbnail
    
    def getProductImages(): # Return product images for displyaing in main product page
        pass

    def updateProduct():
        pass
    
    def deleteProduct():
        pass


class Product:
    def __init__(self, name, price, stock, release_date, description, images, tags):
        self.name = name
        self.price = price
        self.stock = stock
        self.release_date = release_date
        self.description = description
        self.images = images
        self.tags = tags


def getImageData(file):
    return file.read(), file.mimetype 

connection = DatabaseConnection('localhost', 'root', '', '261_final_test')

@app.route('/thumbnail/<int:productId>')
def thumbnail(productId):
    thumbnail = connection.getProductThumbnail(productId)
    # Response(getImage, getMimetype)
    return Response(thumbnail['image'], mimetype=thumbnail['mimetype'])

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        try:
            thumbnailIndex = int(request.form.get('thumbnail-index'))
            imagesArray = list(map(getImageData, request.files.getlist('images')))

            product = Product(
                name=request.form.get('name'),
                price=request.form.get('price'),
                stock=request.form.get('stock'),
                release_date=request.form.get('release'),
                description=request.form.get('description'),
                images=imagesArray,
                tags=request.form.get('tags').split(', '),
            )

            print(f'name: {product.name}:{type(product.name)}, price: {product.price}:{type(product.price)},\
                stock: {product.stock}:{type(product.stock)}, release: {product.release_date}:{type(product.release_date)},\
                description: {product.description}:{type(product.description)}')

            # Swap images[0] with images[thumbnail-index]
            imageAtZero = product.images[0]
            product.images[0] = product.images[thumbnailIndex]
            product.images[thumbnailIndex] = imageAtZero 

            connection.addProduct(product)
            return redirect(url_for('test'), 200) 

        except Exception as error:
            return render_template('error.html', error=error)

    if request.method == 'GET':
        products = connection.getProductListings()

        if len(products) > 0:
            return render_template('test.html', products=products)
        return render_template('test.html')