from flask_restful import Resource, Api, fields, reqparse
from .models import *
from .database import db
from flask import current_app as app
import werkzeug
from flask import jsonify, make_response
from flask import abort
from flask_login import current_user
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, utils
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


user_datastore = SQLAlchemyUserDatastore(db, user, role)


class RegisterAPI(Resource):
    def post(self):
        try:
            create_user_parser = reqparse.RequestParser()
            create_user_parser.add_argument('username')
            create_user_parser.add_argument('name')
            create_user_parser.add_argument('email')
            create_user_parser.add_argument('password')
            args = create_user_parser.parse_args()
            uname = args.get("username", None)
            email = args.get("email", None)
            password = args.get("password", None)
            name = args.get("name", None)
            user1 = db.session.query(user).filter_by(id=uname).one_or_none()
            if(user1==None):
                user1 = user_datastore.create_user(id=uname,email=email,password=utils.hash_password(password),name=name)
                db.session.commit()
                return make_response(jsonify(msg="Created"), 201)
            else:
                return make_response(jsonify(msg="Email/Username Already Exists"),400)
        except:
            return make_response("Internal Server Error Occurred", 500)

class LoginAPI(Resource):
    def post(self):
        try:
            login_user_parser = reqparse.RequestParser()
            login_user_parser.add_argument('username')
            login_user_parser.add_argument('password')
            args = login_user_parser.parse_args()
            uname = args.get("username", None)
            password = args.get("password", None)
            user1 = db.session.query(user).filter_by(id=uname).first()
            if(user1 and utils.verify_password(password, user1.password)):
                #utils.login_user(user1, remember=True)
                #access_token = current_user.get_auth_token()
                access_token = create_access_token(identity=user1.id)
                return make_response(jsonify(username=user1.id, access_token=access_token), 200) 
            elif(user1==None or not utils.verify_password(password, user1.password)):
                return make_response(jsonify(msg="Bad Username or Password"),401)
            else:
                return make_response(jsonify(msg="Error Occurred"),400)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

class TrackersAPI(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            all_trackers = db.session.query(tracker).filter_by(user_id=user_id).all()
            if all_trackers:
                final_resp = []
                for trkr in all_trackers:
                    trk_typ = db.session.query(trak_type).filter_by(traktypeid=trkr.trk_type).first().trak_type
                    if(trk_typ != 'Multiple Choice'):
                        data = {
                            'id': trkr.trk_id,
                            'name': trkr.trk_name,
                            'description': trkr.description,
                            'type': trk_typ,
                            'settings': ''
                        }
                    else:
                        values = db.session.query(multiplechoice).filter_by(trk_id=trkr.trk_id).all()
                        data = {
                            'id': trkr.trk_id,
                            'name': trkr.trk_name,
                            'description': trkr.description,
                            'type': trk_typ,
                            'settings': [i.value for i in values]
                        }
                    final_resp.append(data)
                return make_response(jsonify(final_resp), 200)
            else:
                return make_response(jsonify(msg="The Resource was not Found on this Server"),404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)
    
    @jwt_required()
    def post(self):
        create_tracker_parser = reqparse.RequestParser()
        create_tracker_parser.add_argument('name')
        create_tracker_parser.add_argument('description')
        create_tracker_parser.add_argument('settings', type=str, action='append')
        create_tracker_parser.add_argument('type')

        args = create_tracker_parser.parse_args()
        name = args.get('name', None)
        description = args.get('description', None)
        settings = args.get('settings', None)
        trk_type = args.get('type', None)
        
        try:
            user_id = get_jwt_identity()
            # get the new tracker's object
            new_tracker = tracker(trk_name = name, description = description, trk_type=trk_type, user_id=user_id)
            # add the detais of new tracker to database session
            db.session.add(new_tracker)
            # flushes the session, so we get the new tracker's id from database, without committing to disc yet.
            db.session.flush()

            # get all the settings, remove spaces and split by comma
            if(trk_type == '3'):
                if(settings != None):
                    s = ", ".join(settings)
                    new_tracker.settings = s
                    for i in settings:
                        # make settings object
                        new_setting = multiplechoice(trk_id=new_tracker.trk_id, value=i)
                        # add the details of new settings to db session
                        db.session.add(new_setting)
                        # flushes the session, so we get the new tracker's id from database, without committing to disc yet.
                        db.session.flush()
                else:
                    return make_response(jsonify(msg="Choices are required with this type of tracker."), 400)
            # commit all the changes commited to settings so far
            db.session.commit()
            return make_response(jsonify({"msg": "Tracker Added"}), 201)
        except:
            # rollback whatever the last session changes were.
            db.session.rollback()            
            # set error flash message
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

class OneTrackerAPI(Resource):
    @jwt_required()
    def get(self, trk_id):
        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=trk_id).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                trk_typ = db.session.query(trak_type).filter_by(traktypeid=trkr.trk_type).first().trak_type
                if(trk_typ != 'Multiple Choice'):
                    data = {
                        'id': trkr.trk_id,
                        'name': trkr.trk_name,
                        'description': trkr.description,
                        'type': trk_typ,
                        'settings': ''
                    }
                else:
                    values = db.session.query(multiplechoice).filter_by(trk_id=trkr.trk_id).all()
                    data = {
                        'id': trkr.trk_id,
                        'name': trkr.trk_name,
                        'description': trkr.description,
                        'type': trk_typ,
                        'settings': [i.value for i in values]
                        }
                return make_response(jsonify(data), 200)
            else:
                return make_response(jsonify(msg="The Requested Resource was not Found"), 404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)
    
    @jwt_required()
    def delete(self, trk_id):
        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=trk_id).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                db.session.query(tracker).filter_by(trk_id=trk_id).delete()
                db.session.query(log).filter_by(trk_id=trk_id).delete()
                db.session.query(multiplechoice).filter_by(trk_id=trk_id).delete()
                db.session.commit()
                return make_response(jsonify(msg="Success"), 200)
            else:
                return make_response(jsonify(msg="Not Found"), 404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

    @jwt_required()
    def patch(self, trk_id):

        patch_tracker_parser = reqparse.RequestParser()
        patch_tracker_parser.add_argument('name')
        patch_tracker_parser.add_argument('description')
        patch_tracker_parser.add_argument('settings', type=str, action='append')
        patch_tracker_parser.add_argument('type')

        args = patch_tracker_parser.parse_args()
        name = args.get('name', None)
        description = args.get('description', None)
        settings = args.get('settings', None)
        trk_type = args.get('type', None)

        #print(int(trk_id))

        try:
            user_id = get_jwt_identity()
            trac = db.session.query(tracker).filter_by(trk_id=int(trk_id)).first()
            if(not trac):
                return make_response(jsonify(msg="Not Found"), 404)
            if(trac.user_id != user_id):
                return make_response("Forbidden/Unauthorised Access",403)
            trac.trk_name = name
            trac.description = description
            trac.trk_type = trk_type
        
            if(trk_type == '3'):
                if(settings != None):
                    s = ", ".join(settings)
                    trac.settings = s
                    for i in settings:
                        # make settings object
                        new_setting = multiplechoice(trk_id=trac.trk_id, value=i)
                        # add the details of new settings to db session
                        db.session.add(new_setting)
                        # flushes the session, so we get the new tracker's id from database, without committing to disc yet.
                        db.session.flush()
            else:
                trac.settings = None
            db.session.commit()
            return make_response(jsonify(msg="Success"),200)
        except:
            db.session.rollback() 
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)


class LogsAPI(Resource):
    @jwt_required()
    def get(self,trk_id):
        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=trk_id).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                all_logs = db.session.query(log).filter_by(trk_id=trk_id).all()
                if all_logs:
                    final_resp = []
                    for logone in all_logs:
                        data = {
                            'id': logone.log_id,
                            'timestamp': logone.time,
                            'note': logone.note,
                            'value': logone.value,
                        }
                        final_resp.append(data)
                    return make_response(jsonify(final_resp),200)
                else:
                    return make_response(jsonify(msg="Not Found"), 404)
            else:
                return make_response(jsonify(msg="Not Found"), 404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

    @jwt_required()
    def post(self, trk_id):
        create_log_parser = reqparse.RequestParser()
        create_log_parser.add_argument('note')
        create_log_parser.add_argument('value')

        args = create_log_parser.parse_args()
        note = args.get('note', None)
        value = args.get('value', None)

        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=int(trk_id)).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                lg = log(trk_id=trk_id, user_id=user_id, value=value, time=func.now(), note=note)
                db.session.add(lg)
                db.session.commit()
                return make_response(jsonify(msg="Success"), 200)
            else:
                return make_response(jsonify(msg="Not Found"), 404)
        except:
            db.session.rollback()
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

class OneLogAPI(Resource):
    @jwt_required()
    def get(self,trk_id,log_id):
        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=trk_id).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                logone = db.session.query(log).filter_by(log_id=log_id).first()
                if(logone.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                if logone:
                    data = {
                            'id': logone.log_id,
                            'timestamp': logone.time,
                            'note': logone.note,
                            'value': logone.value
                            }
                    return make_response(jsonify(data),200)
                else:
                    return make_response(jsonify(msg="Log Not Found"), 404)
            else:
                return make_response(jsonify(msg="Tracker Not Found"), 404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

    @jwt_required()
    def delete(self, trk_id, log_id):
        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=trk_id).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                logone = db.session.query(log).filter_by(log_id=log_id).first()
                if logone:
                    if(logone.user_id != user_id):
                        return make_response("Forbidden/Unauthorised Access",403)
                    db.session.query(log).filter_by(log_id=log_id).delete()
                    db.session.commit()
                    return make_response(jsonify(msg="Success"),200)
                else:
                    return make_response(jsonify(msg="Log Not Found"), 404)
            else:
                return make_response(jsonify(msg="Tracker Not Found"), 404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)

    @jwt_required()
    def patch(self, trk_id, log_id):
        patch_log_parser = reqparse.RequestParser()
        patch_log_parser.add_argument('note')
        patch_log_parser.add_argument('value')

        args = patch_log_parser.parse_args()
        note = args.get('note', None)
        value = args.get('value', None)

        try:
            user_id = get_jwt_identity()
            trkr = db.session.query(tracker).filter_by(trk_id=trk_id).first()
            if trkr:
                if(trkr.user_id != user_id):
                    return make_response("Forbidden/Unauthorised Access",403)
                logone = db.session.query(log).filter_by(log_id=log_id).first()
                if logone:
                    if(logone.user_id != user_id):
                        return make_response("Forbidden/Unauthorised Access",403)
                    db.session.query(log).filter((log.trk_id==trk_id) & (log.log_id==log_id)).update({'value': value, 'note':note})
                    db.session.commit()
                    return make_response(jsonify(msg="Success"),200)
                else:
                    return make_response(jsonify(msg="Log Not Found"), 404)
            else:
                return make_response(jsonify(msg="Tracker Not Found"), 404)
        except:
            return make_response(jsonify(msg="Internal Server Error Occurred"), 500)