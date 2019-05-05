from flask import current_app, g
from flask.cli import with_appcontext
from pymongo import MongoClient
import urllib.parse

def get_db():
    client = MongoClient("mongodb+srv://jpDev:" + urllib.parse.quote_plus('Inert@Watch!Battery') + "@cluster-jp1-cknzk.mongodb.net/test?retryWrites=true")
    db = client.test

    return db
