from flask import Flask,render_template,request,redirect
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os
from datetime import datetime
from .plotforapp import *
from .database import db
from .models import *




@app.route("/",methods = ["GET", "POST"])
def home():    
    return(render_template("homepage.html"))


@app.route("/signup",methods = ["GET","POST"])
def signup():
    if(request.method == "GET"):
        return(render_template("signup.html",err="Pick a Username"))
    elif(request.method == "POST"):
        req = request.form
        fname = req.get("fname")
        uname = req.get("uname")
        #redirect to the errorpage if already exists
        if(len(user.query.filter_by(user_id=uname).all())!=0):
           return(render_template("signup.html",err="Username Already Exists, Pick another Username!"))
        #but before that take in the data into the database
        us = user(user_id=uname,name=fname)
        db.session.add(us)
        db.session.commit()
        #redirect to  dashboard
        return(redirect("/"+uname+"/dashboard"))


@app.route("/login",methods = ["GET","POST"])
def login():
    if(request.method == "GET"):
        return(render_template("login.html",err="Welcome Back!"))
    elif(request.method == "POST"):
        req = request.form
        uname = req.get("uname")
        #check if account exists
        if(len(user.query.filter_by(user_id=uname).all())==0):
            return(render_template("login.html",err="No Such Username Exists"))
        #if no account send no account exists message
        #else to dashboard
        us = user.query.filter_by(user_id=uname).first()
        return(redirect("/"+uname+"/dashboard"))


@app.route("/<string:uname>/dashboard",methods = ["GET","POST"])
def dashboard(uname):
    #find username in db
    user1 = db.session.query(user).filter_by(user_id=uname).first()
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
    return(render_template("dash.html",uname=user1.name,userid=user1.user_id, logdic=logdic, trackerlist=trackerlist))


@app.route("/<string:uname>/<int:trackerid>")
def trackerlog(uname,trackerid):
    #get tracker name
    trakr = db.session.query(tracker).filter_by(trk_id=trackerid).first()

    #log list where tracker id = tracker
    loglist = db.session.query(log).filter_by(trk_id=trackerid).all()
    plotgraph(trakr)
    loglist.reverse()
    return(render_template("logs.html",userid=uname, tracker=trakr, loglist=loglist))


@app.route("/<string:uname>/addtracker",methods = ["GET","POST"])
def addtracker(uname):
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
        #add to tracker table(maybe outsource to a function)
        #redirect to that tracker
        return(redirect("/"+uname+"/"+str(track.trk_id)))
    

@app.route("/<string:uname>/<int:trackerid>/delete")
def deletetracker(uname,trackerid):
    db.session.query(tracker).filter_by(trk_id=trackerid).delete()
    db.session.query(log).filter_by(trk_id=trackerid).delete()
    db.session.query(multiplechoice).filter_by(trk_id=trackerid).delete()
    db.session.commit()
    return(redirect("/"+uname+"/dashboard"))

    
@app.route("/<string:uname>/<int:trackid>/update",methods = ["GET","POST"])
def updatetracker(uname,trackid):
    if(request.method=="GET"):
        track = db.session.query(tracker).filter_by(trk_id=trackid).first()
        return(render_template("updatetracker.html",tracker=track, userid=uname))
    elif(request.method=="POST"):
        #still need to update
        req = request.form
        name = req.get("trakname")
        desc = req.get("trakdesc")
        trac = db.session.query(tracker).filter_by(trk_id=trackid).first()
        trac.trk_name = name
        trac.description = desc
        db.session.commit()
        return(redirect("/"+uname+"/dashboard"))


@app.route("/<string:uname>/<int:trackid>/addlog",methods = ["GET","POST"])
def addlog(uname,trackid):
    track = db.session.query(tracker).filter_by(trk_id=trackid).first()
    if(request.method=="GET"):
        value=[]
        if(track.trk_type==3):
            value=db.session.query(multiplechoice).filter_by(trk_id=trackid).all()
        return(render_template("addlog.html",track=track, values=value, userid=uname))
    elif(request.method=="POST"):
        tracktype = track.trk_type
        req = request.form
        #tracker
        #user
        #time
        #note
        note = req.get("message")
        val = req.get("value")
        if(val == "Other"):
          newmcqval = req.get("other")
          mcq = multiplechoice(trk_id=trackid, value=newmcqval)
          val = newmcqval
          db.session.add(mcq)
          db.session.commit()
        lg = log(trk_id=trackid, user_id=uname, value=val, time=func.now(), note=note)
        db.session.add(lg)
        db.session.commit()
        return(redirect("/"+uname+"/"+str(trackid)))

    
@app.route("/<string:uname>/<int:trackid>/<timestamp>/deletelog")
def deletelog(uname,trackid,timestamp):
    db.session.query(log).filter((log.trk_id==trackid) & (log.time==timestamp)).delete()
    db.session.commit()
    return(redirect("/"+uname+"/"+str(trackid)))
    

    
@app.route("/<string:uname>/<int:trackid>/<timestamp>/updatelog", methods = ["GET","POST"])
def updatelog(uname,trackid,timestamp):
    if(request.method == "GET"):
        lg = db.session.query(log).filter((log.trk_id==trackid) & (log.time==timestamp)).first()
        track = db.session.query(tracker).filter_by(trk_id=trackid).first()
        value=[]
        if(track.trk_type==3):
            value=db.session.query(multiplechoice).filter_by(trk_id=trackid).all()
        prevvalue = lg.value
        prevnote = lg.note
        return(render_template("updatelog.html",userid=uname, values=value, prevvalue=prevvalue, prevnote=prevnote, timestamp=timestamp, trackid=trackid, track=track))
    elif(request.method == "POST"):
        req = request.form
        val = req.get("value")
        note = req.get("message")
        db.session.query(log).filter((log.trk_id==trackid) & (log.time==timestamp)).update({'value': val, 'note':note})
        db.session.commit()
        return(redirect("/"+uname+"/"+str(trackid)))
