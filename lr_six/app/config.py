import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = '123123123'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'courses.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
