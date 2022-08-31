import os
from flask import Flask
from madapp.database import db

app = None

def createapp():
    currdir=os.path.abspath(os.path.dirname(__file__))
    app = Flask('__name__', template_folder='templates')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(currdir,"trackerdb.sqlite3")
    db.init_app(app)
    app.app_context().push()
    return(app)

app = createapp()

from madapp.controller import *

if(__name__ == '__main__'):
    app.debug=True
    app.run(host='0.0.0.0')
