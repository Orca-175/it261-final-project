from flask_login import login_user
from app_factory import app, connection
from flask import render_template, request, redirect, url_for
from modules.exceptions import PasswordLengthError, ProductNotFoundError, UserNotFoundError, UsernameTakenError, WrongPasswordError
from models.product import Product

@app.route('/admin_view')
def adminView():
    products = connection.getProductListings()

    if len(products) > 0:
        return render_template('admin_view.html', products=products)
    return render_template('admin_view.html')


# Operations
@app.route('/admin_add_product', methods=['POST'])
def adminAddProduct():
    print(request.form)
    try:
        thumbnailIndex = int(request.form.get('thumbnail-index'))

        product = Product(
            name=request.form.get('name'),
            price=int(request.form.get('price')),
            stock=int(request.form.get('stock')),
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

    except ValueError:
        return 'Number fields must be filled with numeric values.', 400

    except Exception:
        return 'Something went wrong.', 500


@app.route('/admin_edit_product', methods=['POST'])
def adminEditProduct():
    try: 
        productId = int(request.form.get('edit-id').strip()) 
        product = Product(
            name=request.form.get('edit-name'),
            price=int(request.form.get('edit-price')),
            stock=int(request.form.get('edit-stock')),
            releaseDate=request.form.get('edit-release'),
            description=request.form.get('edit-description'),
            images=None,
            tags=request.form.get('edit-tags').split(', '),
        )
        thumbnailIndex = int(request.form.get('thumbnail-index'))

        connection.editProduct(productId, product, thumbnailIndex)
        return redirect(url_for('adminView'))
    
    except ValueError:
        return 'Number fields must be filled with numeric values.', 400
    
    except ProductNotFoundError as error:
        return error, 404

    except Exception:
        return 'Something went wrong.', 500


@app.route('/admin_delete_product', methods=['POST'])
def adminDeleteProduct():
    productId = request.form.get('productId')
    try:
        connection.deleteProduct(int(productId))
        return 'Product deleted!'
    except ProductNotFoundError as error:
        return str(error), 404
    except ValueError:
        return f'"{productId}" is not a valid Product ID.', 400


@app.route('/admin_get_product_details/<productId>')
def getProductDetails(productId):
    try: 
        return connection.getProductDetails(productId)
    except ProductNotFoundError as error:
        return str(error), 404


# Authentication
@app.route('/admin_login', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        try: 
            login_user(connection.authenticateAdmin(request.form.get('username'), request.form.get('password')))
        except UserNotFoundError as error:
            return str(error), 404
        except WrongPasswordError as error:
            return str(error), 400
        except Exception:
            return 'Something went wrong.', 500


@app.route('/admin_registration', methods=['GET', 'POST'])
def adminRegistration():
    if request.method == 'GET':
        return render_template('admin_registration.html')
    if request.method == 'POST':
        if request.form.get('password') != request.form.get('confirm-password'):
            return 'Confirm password does not match password.', 400
        try:
            connection.registerAdmin(request.form.get('username'), request.form.get('password'))
            return redirect()
        except UsernameTakenError as error:
            return str(error), 400
        except PasswordLengthError as error:
            return str(error), 400
        except Exception:
            return 'Something went wrong.', 500