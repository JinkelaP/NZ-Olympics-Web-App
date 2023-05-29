from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__, static_folder='static')

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

# designed a validation of member id
def memberIDValid(member_id):
    connection = getCursor()
    connection.execute('SELECT members.MemberID from members;')
    memberIDList = connection.fetchall()
    for id in memberIDList:
        if id[0] == member_id:
            return True
        
# date convert function

def dateConvert(mySQLConnect):
    while type(mySQLConnect[0]) == tuple:
        listTupleInfo = list(mySQLConnect[0])
        listTupleInfo[1] = listTupleInfo[1].strftime("%d/%m/%Y")
        mySQLConnect.append(listTupleInfo)
        mySQLConnect.pop(0)
                

# redirect all 404 pages to my bootstrapped one.
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html'), 404

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listmembers")
def listmembers():
    connection = getCursor()
    connection.execute("SELECT  members.MemberID, members.FirstName, members.LastName, teams.TeamName, members.City, members.Birthdate \
                       FROM members \
                       INNER JOIN teams ON members.teamID=teams.TeamID \
                       ORDER BY members.MemberID;")
    memberList = connection.fetchall()
    return render_template("memberlist.html", memberlist = memberList)

@app.route("/member/<int:member_id>")
def memberPage(member_id):
    if memberIDValid(member_id) == True:
        connection = getCursor()
        connection.execute(f"SELECT members.teamID, members.FirstName, members.LastName \
                           FROM members\
                           WHERE members.MemberID={member_id}")
        memberInfo = connection.fetchall()
        
        nameMember = memberInfo[0][1] + ' ' + memberInfo[0][2]

        connection = getCursor()
        connection.execute(f"SELECT events.EventName, event_stage.StageDate, event_stage.StageName, event_stage.Location \
                           FROM events\
                           INNER JOIN event_stage ON events.EventID=event_stage.EventID\
                           WHERE events.NZTeam={memberInfo[0][0]}")
        upcomingList = connection.fetchall()

        # convert date

        dateConvert(upcomingList)



        return render_template("member.html",upcominglist=upcomingList,name_member=nameMember)
    else:
        return render_template("404.html")
# designed a validation of member id and 404 page in case that someone type an unavailable number to the link.


@app.route("/listevents")
def listevents():
    connection = getCursor()
    # connection.execute("SELECT * FROM events;")
    connection.execute("SELECT events.EventID, events.EventName, events.Sport, teams.TeamName \
                       FROM events \
                       INNER JOIN teams ON events.NZTeam=teams.TeamID \
                       ORDER BY events.EventID;")
    eventList = connection.fetchall()
    return render_template("eventlist.html", eventlist = eventList)


@app.route("/admin")
def admin():
    return render_template("admin.html")