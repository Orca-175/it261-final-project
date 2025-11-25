from app_factory import app, connection
from flask import Flask, render_template
from modules.exceptions import ProductNotFoundError

# Routes
import admin_routes


@app.route('/search_products/', defaults={'searchQuery': ''})
@app.route('/search_products/<searchQuery>')
def searchProduct(searchQuery):
    return connection.getProductListings('%' + searchQuery + '%')


@app.route('/product/<productId>')
def product(productId):
    try: 
        return render_template('product.html', product=connection.getProductDetails(int(productId)))

    except ProductNotFoundError as error:
        return str(error), 404

    except ValueError:
        return f'"{productId}" is not a valid product id.'


