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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listmembers")
def listmembers():
    connection = getCursor()
    connection.execute("SELECT teams.TeamName, members.FirstName, members.LastName, members.City, members.Birthdate, members.MemberID \
                       FROM members \
                       INNER JOIN teams ON members.teamID=teams.TeamID \
                       ORDER BY teams.TeamName, members.FirstName;")
    memberList = connection.fetchall()
    # print(memberList)
    return render_template("memberlist.html", memberlist = memberList)    


@app.route("/listevents")
def listevents():
    connection = getCursor()
    connection.execute("SELECT * FROM events;")
    eventList = connection.fetchall()
    return render_template("eventlist.html", eventlist = eventList)


@app.route("/admin")
def admin():
    return render_template("admin.html")