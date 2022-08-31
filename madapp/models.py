from .database import db
from sqlalchemy import func

#log stores the logs of all trackers and users
class log(db.Model):
    __tablename__ = 'log'
    trk_id = db.Column(db.Integer, nullable=False,primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)
    time = db.Column(db.DateTime(timezone=True), server_default=func.now(),primary_key=True)
    note = db.Column(db.String)

class multiplechoice(db.Model):
    __tablename__ = 'multiplechoice'
    trk_id = db.Column(db.Integer, nullable=False, primary_key=True)
    value = db.Column(db.String,primary_key=True)

class tracker(db.Model):
    __tablename__ = 'tracker'
    trk_id = db.Column(db.Integer, nullable=False,primary_key=True)
    trk_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    trk_type = db.Column(db.Integer, nullable=False)
    settings = db.Column(db.String)
    user_id = db.Column(db.String, nullable=False)

class trak_type(db.Model):
    __tablename__ = 'trak_type'
    traktypeid = db.Column(db.Integer, nullable=False,primary_key=True)
    trak_type = db.Column(db.String)

class user(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
