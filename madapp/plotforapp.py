import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .database import db
from .models import *


def plotgraph(track):
    loglist = db.session.query(log).filter_by(trk_id=track.trk_id).order_by(log.time).all()
    tracktype = track.trk_type
    if(tracktype==1):
        plotnum(loglist,track)
    if(tracktype==2):
        plotbool(loglist,track)
    elif(tracktype==3):
        multi = db.session.query(multiplechoice).filter_by(trk_id=track.trk_id).all()
        plotmc(loglist,track,multi)
    elif(tracktype==4):
        plottime(loglist,track)

def plotnum(loglist,track):
    plt.clf()
    values = []
    times = []
    for x in loglist:
        values.append(float(x.value))
        times.append(x.time.strftime("%d-%m"))
        # plot
    plt.title(track.trk_name+" Trendline")
    plt.xlabel("Count")
    plt.ylabel("Dates")
    plt.plot(times,values, linewidth=2.0, c='#653187',marker='o' )
    plt.grid(color='#ffbbb1')
        #plt.plot(times,values)
    plt.savefig('static/plot.jpg')

def plotbool(loglist,track):#bargraph
    plt.clf()
    values=["Yes","No"]
    count=[0,0]
    for x in loglist:
        if(x.value=="Yes"):
            count[0]+=1
        elif(x.value=="No"):
            count[1]+=1
    plt.title(track.trk_name+" Trendline")
    plt.xlabel("Value")
    plt.ylabel("Count")
    plt.bar(values,count, color='#653187', width=0.4 )
        #plt.plot(times,values)
    plt.savefig('static/plot.jpg')

def plotmc(loglist,track,multi):#bargraph
    plt.clf()
    choices = []
    choicesid = []
    count = []
    for x in multi:
        choices.append(x.value)
    for x in choices:
        count.append(0)
        for y in loglist:
            if(y.value==x):
                count[-1]+=1
    plt.title(track.trk_name+" Trendline")
    plt.xlabel("Values")
    plt.ylabel("Count")
    plt.bar(choices, count, color='#653187', width=0.4 )
        #plt.plot(times,values)
    plt.savefig('static/plot.jpg')
    
def plottime(loglist,track):#plot with duration and dates
    plt.clf()
    values = []
    times = []
    for x in loglist:
        values.append(x.value)
        times.append(x.time.strftime("%d-%m"))
    plt.title(track.trk_name+" Trendline")
    plt.xlabel("Duration")
    plt.ylabel("Dates")
    plt.plot(times,values, linewidth=2.0, c='#653187',marker='o' )
    plt.grid(color='#ffbbb1')
        #plt.plot(times,values)
    plt.savefig('static/plot.jpg')



