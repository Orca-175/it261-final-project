from flask_login import login_required, login_user, current_user, logout_user
from app_factory import app, connection
from flask import flash, jsonify, render_template, request, redirect, url_for
from modules.exceptions import AccountAlreadyApprovedError, PasswordLengthError, ProductNotFoundError, UserNotFoundError, UsernameTakenError, WrongPasswordError
from models.product import Product


@app.route('/admin_products_view')
@login_required
def adminProductsView():
    if current_user.role != 'admin':
        flash('Unauthorized role. Please login to an admin account to access this page.', 'error')
        return redirect(url_for('adminLogin'), 403)

    products = connection.getProductListings()

    return render_template('admin_products_view.html', products=products)


@app.route('/admin_users_view')
@login_required
def adminUsersView():
    if current_user.role != 'admin':
        flash('Unauthorized role. Please login to an admin account to access this page.', 'error')
        return redirect(url_for('adminLogin'), 403)
    
    users = connection.getAdmins()

    return render_template('admin_users_view.html', users=users)


# Operations
@app.route('/admin_add_product', methods=['POST'])
@login_required
def adminAddProduct():
    if current_user.role != 'admin':
        return 'Unauthorized role.', 401

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
@login_required
def adminEditProduct():
    if current_user.role != 'admin':
        return 'Unauthorized role.', 401

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
@login_required
def adminDeleteProduct():
    if current_user.role != 'admin':
        return 'Unauthorized role.', 401

    productId = request.form.get('productId')
    try:
        connection.deleteProduct(int(productId))
        return 'Product deleted!'
    except ProductNotFoundError as error:
        return str(error), 404
    except ValueError:
        return f'"{productId}" is not a valid Product ID.', 400


@app.route('/admin_get_product_details/<productId>')
@login_required
def getProductDetails(productId):
    if current_user.role != 'admin':
        return 'Unauthorized role.', 401

    try: 
        return connection.getProductDetails(productId)
    except ProductNotFoundError as error:
        return str(error), 404


@app.route('/approve_user', methods=['POST'])
@login_required
def approveUser():
    if current_user.role != 'admin':
        return 'Unauthorized role.', 401
    
    adminId = request.form.get('admin-id')
    try:
        connection.approveAdmins(int(adminId))
        return 'Account has been approved!'
    except ValueError:
        return f'"{adminId}" is not a valid account id.', 400
    except AccountAlreadyApprovedError:
        username = connection.getAdmin(adminId).username
        return f'"{username}" is already approved.', 400


@app.route('/get_admins')
@login_required
def getAdmins():
    if current_user.role != 'admin':
        return 'Unauthorized role.', 401

    try:
        return connection.getAdmins()
    except Exception:
        return 'Something went wrong.', 500



# Authentication
@app.route('/admin_login', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == '' or password == '':
            return 'Empty inputs detected. Please fill in all fields.', 400

        try: 
            if not login_user(connection.authenticateAdmin(username, password)):
                return 'User has not been approved.', 401
            return jsonify({'redirect': url_for('adminProductsView')})
        except UserNotFoundError as error:
            return str(error), 404
        except WrongPasswordError as error:
            return str(error), 400
        except Exception as error:
            return f'Something went wrong. {error}', 500


@app.route('/admin_registration', methods=['GET', 'POST'])
def adminRegistration():
    if request.method == 'GET':
        return render_template('admin_registration.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm-password')

        if username == '' or password == '' or confirmPassword == '':
            return 'Empty inputs detected. Please fill in all fields.', 400
        if password != confirmPassword:
            return 'Confirm password does not match password.', 400

        try:
            connection.registerAdmin(username, password)
            return jsonify({'redirect': url_for('adminLogin')}) 
        except UsernameTakenError as error:
            return str(error), 400
        except PasswordLengthError as error:
            return str(error), 400
        except Exception:
            return 'Something went wrong.', 500


@app.route('/admin_logout')
@login_required
def adminLogout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('adminLogin'))