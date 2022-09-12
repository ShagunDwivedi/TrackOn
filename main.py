import os
from flask import Flask
from madapp.database import db
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from flask_restful import Api
from flask_jwt_extended import JWTManager
from madapp.models import user, role
from madapp.for_security import *

app = None
api = None

def createapp():
    currdir=os.path.abspath(os.path.dirname(__file__))
    app = Flask('__name__', template_folder='templates')
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(currdir,"trackerdb.sqlite3")
    app.config["SECRET_KEY"] = "verysecretkey"
    app.config["SECURITY_PASSWORD_HASH"] = 'bcrypt'
    app.config["SECURITY_PASSWORD_SALT"] = "reallysupersecret"
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_UNAUTHORIZED_VIEW"] = '/'
    app.config["SECURITY_POST_LOGIN_VIEW"] = '/dashboard'
    app.config["SECURITY_POST_REGISTER_VIEW"] = '/dashboard'
    app.config['JWT_SECRET_KEY'] = 'SECURITY_SECRET'
    app.config['JWT_TOKEN_LOCATION'] = 'headers'
    #app.config['JSON_SORT_KEYS'] = False

    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    user_datastore = SQLAlchemySessionUserDatastore(db.session, user, role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
    return(app, api)

app, api = createapp()
jwt = JWTManager(app)

from madapp.controller import *
from madapp.api import *
 
api.add_resource(RegisterAPI, "/api/signup")
api.add_resource(LoginAPI, "/api/login")
api.add_resource(TrackersAPI, "/api/trackers")
api.add_resource(OneTrackerAPI, "/api/tracker/<int:trk_id>")
api.add_resource(LogsAPI, "/api/tracker/<int:trk_id>/logs")
api.add_resource(OneLogAPI,"/api/tracker/<int:trk_id>/logs/<int:log_id>")


if(__name__ == '__main__'):
    app.debug=True
    app.run(host='0.0.0.0')
