from flask import Flask, render_template, request, redirect, url_for
from modules.database_connection import DatabaseConnection
from modules.image_storage_handler import ImageStorageHandler
from modules.models import Product

app = Flask(__name__)


connection = DatabaseConnection(
    'localhost', 
    'root', 
    '', 
    '261_final_test', 
    ImageStorageHandler('static/images')
)


@app.route('/admin_view')
def adminView():
    products = connection.getProductListings()

    if len(products) > 0:
        return render_template('admin_view.html', products=products)
    return render_template('admin_view.html')


@app.route('/admin_add_product', methods=['POST'])
def adminAddProduct():
    try:
        thumbnailIndex = int(request.form.get('thumbnail-index'))

        product = Product(
            name=request.form.get('name'),
            price=request.form.get('price'),
            stock=request.form.get('stock'),
            releaseDate=request.form.get('release'),
            description=request.form.get('description'),
            images=request.files.getlist('images'),
            tags=request.form.get('tags').split(', ')
        )

        # Swap images[0] with images[thumbnail-index]
        imageAtZero = product.images[0]
        product.images[0] = product.images[thumbnailIndex]
        product.images[thumbnailIndex] = imageAtZero 

        connection.addProduct(product)
        return redirect(url_for('adminView')) 

    except Exception as error:
        return render_template('error.html', error=error)


@app.route('/admin_edit_product', methods=['POST'])
def adminEditProduct():
    try: 
        productId = request.form.get('edit-id').strip()
        product = Product(
            name=request.form.get('edit-name'),
            price=request.form.get('edit-price'),
            stock=request.form.get('edit-stock'),
            releaseDate=request.form.get('edit-release'),
            description=request.form.get('edit-description'),
            images=None,
            tags=request.form.get('edit-tags').split(', '),
        )
        thumbnailIndex = int(request.form.get('thumbnail-index'))

        connection.editProduct(productId, product, thumbnailIndex)
        return redirect(url_for('adminView'))
    except Exception as error:
        return render_template('error.html', error=error)


@app.route('/admin_delete_product', methods=['POST'])
def adminDeleteProduct():
    productId = request.form.get('productId')
    try:
        connection.deleteProduct(int(productId))
        return 'Product deleted!'
    except Exception:
        return f'Product {productId} could not be deleted.', 400


@app.route('/admin_get_product_details/<productId>')
def getProductDetails(productId):
    return connection.getProductDetails(productId)


@app.route('/search_products/', defaults={'searchQuery': ''})
@app.route('/search_products/<searchQuery>')
def searchProduct(searchQuery):
    return connection.getProductListings('%' + searchQuery + '%')


@app.route('/product/<productId>')
def product(productId):
    return render_template('product.html', product=connection.getProductDetails(productId))