from .database import db
from sqlalchemy import func
from flask_security import UserMixin, RoleMixin


#log stores the logs of all trackers and users
class log(db.Model):
    __tablename__ = 'log'
    log_id = db.Column(db.Integer, nullable=False,primary_key=True)
    trk_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)
    time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    note = db.Column(db.String)

#multiplechoice stores the values for multiple choice trackers
class multiplechoice(db.Model):
    __tablename__ = 'multiplechoice'
    trk_id = db.Column(db.Integer, nullable=False, primary_key=True)
    value = db.Column(db.String,primary_key=True)

#tracker stores tracker details
class tracker(db.Model):
    __tablename__ = 'tracker'
    trk_id = db.Column(db.Integer, nullable=False,primary_key=True)
    trk_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    trk_type = db.Column(db.Integer, nullable=False)
    settings = db.Column(db.String)
    user_id = db.Column(db.String, nullable=False)

#trak_type stores details about the types of trackers available
class trak_type(db.Model):
    __tablename__ = 'trak_type'
    traktypeid = db.Column(db.Integer, nullable=False,primary_key=True)
    trak_type = db.Column(db.String)

#because ofcourse
roles_user = db.Table('roles_user',
    db.Column('user_id', db.String, db.ForeignKey('user.id')),
    db.Column('role_id', db.String, db.ForeignKey('role.id')))

#user stores user details
class user(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    roles = db.relationship('role', secondary=roles_user,backref=db.backref('user', lazy='dynamic'))

#role model as per flask-security
class role(db.Model, RoleMixin):
    __tablename__= 'role'
    id = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String, default="app_user")

