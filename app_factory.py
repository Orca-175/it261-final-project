from flask import Flask, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from modules.database_connection import DatabaseConnection
from modules.image_storage_handler import ImageStorageHandler

app = Flask(__name__)
app.secret_key = '3550fbdb801fc78221ba1c15a4a3f096839c06424ce4bfd35d6ebc1ee7e41982'

loginManager = LoginManager(app)
loginManager.login_view = 'adminLogin'
loginManager.init_app(app)
bcrypt = Bcrypt(app)    

connection = DatabaseConnection(
    'localhost', 
    'root', 
    '', 
    'beta_glitch', 
    ImageStorageHandler('static/images')
)



@loginManager.user_loader
def userLoader(userId):
    role, id = userId.split('.')
    if role == 'customer':
        return connection.getCustomer(id)
    if role == 'admin':
        return connection.getAdmin(id)
