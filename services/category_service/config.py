import os

class Config:
    # Update username, password, host, db name
    SQLALCHEMY_DATABASE_URI = "mysql://root:password@localhost/categoriesdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev_secret_key"
