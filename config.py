import os

# Settings for the Flask app

class Config:
    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:Red$hop2024!@localhost/redshop'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    ALLOWED_EXTENSIONS = {'svg', 'png', 'jpg', 'jpeg'}
    UPLOAD_FOLDER = 'static/uploads'

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS