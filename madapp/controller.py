from flask import Flask,render_template,request,redirect
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_security import login_required
from flask_login import current_user
import os
from datetime import datetime
from .plotforapp import *
from .database import db
from .models import *


def get_uname():
    user1 = current_user
    return user1.id

@app.route("/",methods = ["GET", "POST"])
def home():    
    return(render_template("homepage.html"))


@app.route("/dashboard",methods = ["GET","POST"])
@login_required
def dashboard():
    #find username in db
    uname = get_uname()
    #print(uname)

    #user1 = db.session.query(user).filter_by(user_id=uname).first()
    #link to tracker table
    trackerlist = db.session.query(tracker).filter_by(user_id=uname).all()
    #get the last log out of all the trackers
    logdic={}
    if(len(trackerlist)!=0):
        for trkr in trackerlist:
            z = db.session.query(log).filter((log.trk_id==trkr.trk_id) & (log.user_id==uname)).all() #also add user=user
            if(len(z)!=0):
                #print(z[-1])
                if(trkr in logdic):
                    logdic[trkr].append(z[-1])
                else:
                    logdic[trkr]=[z[-1]]
            #take tracker.name into there
    #print(logdic[trackerlist[0]][0].note)
    return(render_template("dash.html",uname=current_user.name,userid=uname, logdic=logdic, trackerlist=trackerlist))


@app.route("/<int:trackerid>")
@login_required
def trackerlog(trackerid):
    #get tracker name
    uname = get_uname()

    trakr = db.session.query(tracker).filter_by(trk_id=trackerid).first()

    #log list where tracker id = tracker
    loglist = db.session.query(log).filter_by(trk_id=trackerid).all()
    plotgraph(trakr)
    loglist.reverse()
    return(render_template("logs.html",userid=uname, tracker=trakr, loglist=loglist))


@app.route("/addtracker",methods = ["GET","POST"])
@login_required
def addtracker():
    uname = get_uname()
    if(request.method == "GET"):
        return(render_template("addtracker.html", userid=uname))
    elif(request.method == "POST"):
        #return()
        #parsing request
        req = request.form
        trackername = req.get("trakname")
        trackdesc = req.get("trakdesc")
        tracktype = req.get("trak_type")
        setting = None
        z=False
        if(tracktype=="3"):
            setting = req.get("settings")
            z = setting.split(",")
        t = tracker(trk_name=trackername, description=trackdesc, trk_type=tracktype, settings=setting, user_id=uname)
        db.session.add(t)
        db.session.commit()
        track = db.session.query(tracker).filter((tracker.trk_name==trackername) & (tracker.user_id==uname)).all()
        track = track[-1]
        if(z):
            for x in z:
                if(x!=''):
                    mcq = multiplechoice(trk_id=track.trk_id, value=x)
                    db.session.add(mcq)
                    db.session.commit()
        #add to tracker table
        #redirect to that tracker
        return(redirect("/"+str(track.trk_id)))
    

@app.route("/<int:trackerid>/delete")
@login_required
def deletetracker(trackerid):
    db.session.query(tracker).filter_by(trk_id=trackerid).delete()
    db.session.query(log).filter_by(trk_id=trackerid).delete()
    db.session.query(multiplechoice).filter_by(trk_id=trackerid).delete()
    db.session.commit()
    return(redirect("/dashboard"))

    
@app.route("/<int:trackid>/update",methods = ["GET","POST"])
@login_required
def updatetracker(trackid):
    uname = get_uname()
    if(request.method=="GET"):
        track = db.session.query(tracker).filter_by(trk_id=trackid).first()
        track_type = db.session.query(trak_type).all()
        return(render_template("updatetracker.html",tracker=track, userid=uname, track_type=track_type))
    elif(request.method=="POST"):
        #still need to update 
        req = request.form
        name = req.get("trakname")
        desc = req.get("trakdesc")
        trk_type = req.get("trak_type")
        trac = db.session.query(tracker).filter_by(trk_id=trackid).first()
        trac.trk_name = name
        trac.description = desc
        trac.trk_type = trk_type
        db.session.commit()
        if(trk_type=="3"):
            db.session.query(multiplechoice).filter_by(trk_id=trackid).delete()
            setting = req.get("settings")
            z = setting.split(",")
            for x in z:
                if(x!=''):
                    mcq = multiplechoice(trk_id=trackid, value=x)
                    db.session.add(mcq)
                    db.session.commit()
        db.session.query(log).filter(log.trk_id==trackid).delete()
        db.session.commit()
        return(redirect("/dashboard"))


@app.route("/<int:trackid>/addlog",methods = ["GET","POST"])
@login_required
def addlog(trackid):
    uname = get_uname()
    track = db.session.query(tracker).filter_by(trk_id=trackid).first()
    if(request.method=="GET"):
        value=[]
        if(track.trk_type==3):
            value=db.session.query(multiplechoice).filter_by(trk_id=trackid).all()
        return(render_template("addlog.html",track=track, values=value))
    elif(request.method=="POST"):
        req = request.form
        #tracker
        #user
        #time
        #note
        note = req.get("message")
        val = req.get("value")
        lg = log(trk_id=trackid, user_id=uname, value=val, time=func.now(), note=note)
        db.session.add(lg)
        db.session.commit()
        return(redirect("/"+str(trackid)))

    
@app.route("/<int:trackid>/<int:logid>/deletelog")
@login_required
def deletelog(trackid,logid):
    db.session.query(log).filter((log.trk_id==trackid) & (log.log_id==logid)).delete()
    db.session.commit()
    return(redirect("/"+str(trackid)))
    

    
@app.route("/<int:trackid>/<int:logid>/updatelog", methods = ["GET","POST"])
@login_required
def updatelog(trackid,logid):
    uname = get_uname()
    if(request.method == "GET"):
        lg = db.session.query(log).filter((log.trk_id==trackid) & (log.log_id==logid)).first()
        track = db.session.query(tracker).filter_by(trk_id=trackid).first()
        value=[]
        if(track.trk_type==3):
            value=db.session.query(multiplechoice).filter_by(trk_id=trackid).all()
        prevvalue = lg.value
        prevnote = lg.note
        return(render_template("updatelog.html",userid=uname, values=value, prevvalue=prevvalue, prevnote=prevnote, logid=logid, trackid=trackid, track=track))
    elif(request.method == "POST"):
        req = request.form
        val = req.get("value")
        note = req.get("message")
        db.session.query(log).filter((log.trk_id==trackid) & (log.log_id==logid)).update({'value': val, 'note':note})
        db.session.commit()
        return(redirect("/"+str(trackid)))
