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
        if listTupleInfo[2] is not None:
            listTupleInfo[2] = listTupleInfo[2].strftime("%d/%m/%Y")
        mySQLConnect.append(listTupleInfo)
        mySQLConnect.pop(0)
                

# redirect all 404 pages to my bootstrapped one.
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html'), 404

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/member")
def member():
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
        # Show name
        connection = getCursor()
        connection.execute("SELECT members.FirstName, members.LastName \
                           FROM members\
                           WHERE members.MemberID=%s;", (member_id,))
        memberInfo = connection.fetchall()
        
        nameMember = memberInfo[0][0] + ' ' + memberInfo[0][1]

        # Show upcoming events
        connection.execute("SELECT events.EventName, events.Sport, event_stage.StageDate, event_stage.StageName, event_stage.Location, event_stage_results.Position \
                           FROM events\
                           JOIN event_stage ON events.EventID=event_stage.EventID\
                           JOIN event_stage_results ON event_stage.StageID = event_stage_results.StageID\
                           WHERE event_stage_results.PointsScored IS NULL and event_stage_results.memberID=%s;",(member_id,))
        upcomingList = connection.fetchall()
        # convert date
        if upcomingList != []:
            dateConvert(upcomingList)
        else:
            upcomingList = None

        # Show previous results
        connection.execute("SELECT events.EventName, events.Sport, event_stage.StageDate, event_stage.StageName, event_stage.Location, event_stage_results.Position, event_stage_results.PointsScored, event_stage_results.StageID \
                           FROM events\
                           JOIN event_stage ON events.EventID=event_stage.EventID\
                           JOIN event_stage_results ON event_stage.StageID = event_stage_results.StageID\
                           WHERE event_stage_results.PointsScored IS NOT NULL and event_stage_results.MemberID=%s;",(member_id,))
        previousListFull = connection.fetchall()
        
        if previousListFull != []:
        # convert date
            dateConvert(previousListFull)
      
        # convert positions to medals or qualifying status
        for memberResult in previousListFull:
            if memberResult[5] == 3:
                memberResult[5] = 'Bronze'
            elif memberResult[5] == 2:
                memberResult[5] = 'Silver'
            elif memberResult[5] == 1:
                memberResult[5] = 'Gold'
            elif 'quali' or 'heat' in memberResult[4].lower():

                memberPoints = memberResult[6]
                connection.execute(f'SELECT event_stage.PointsToQualify FROM event_stage \
                                    WHERE event_stage.StageID = {memberResult[7]};')
                qualiPoints = connection.fetchall()[0][0]
                
                if memberPoints is int and qualiPoints is int:
                    if memberPoints >= qualiPoints:
                        memberResult[5] = 'Qualified'
                    else:
                        memberResult[5] = 'Not Qualified'
                else:
                    memberResult[5] = 'N/A'
        
        for list in previousListFull:
            del list[-2:]

        if previousListFull == []:
            previousListFull = None

        return render_template("member.html",upcominglist=upcomingList,name_member=nameMember,previouslist=previousListFull)
    else:
        return render_template("404.html")
# designed a validation of member id and 404 page in case that someone type an unavailable number to the link.


@app.route("/event")
def event():
    connection = getCursor()
    # connection.execute("SELECT * FROM events;")
    connection.execute("SELECT events.EventID, events.EventName, events.Sport, teams.TeamName \
                       FROM events \
                       INNER JOIN teams ON events.NZTeam=teams.TeamID \
                       ORDER BY events.EventID;")
    eventList = connection.fetchall()

    if eventList == []:
        eventList = None
    return render_template("eventlist.html", eventlist = eventList)


@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin/search", methods=["GET"])
def search():
    searchInput = request.args.get('searchinput')

    connection = getCursor()
    connection.execute("SELECT members.memberID, teams.TeamName, members.FirstName, members.LastName FROM members \
                JOIN teams ON teams.TeamID = members.TeamID \
                WHERE MemberID LIKE %s OR FirstName LIKE %s OR LastName LIKE %s \
                ORDER BY TeamName, LastName;",('%' + searchInput + '%','%' + searchInput + '%','%' + searchInput + '%'))
    searchResult1 = connection.fetchall()

    if searchInput == '' or searchResult1 == []:
        searchResult1 = None

    connection.execute("SELECT events.EventID, events.EventName, events.Sport, teams.TeamName FROM events \
                JOIN teams ON teams.TeamID = events.NZTeam \
                WHERE EventID LIKE %s OR EventName LIKE %s OR Sport LIKE %s;"\
                ,('%' + searchInput + '%','%' + searchInput + '%','%' + searchInput + '%'))
    searchResult2 = connection.fetchall()

    if searchInput == '' or searchResult2 == []:
        searchResult2 = None

    return render_template("search.html", searchresult1 = searchResult1, searchresult2 = searchResult2, searchinput = searchInput)

@app.route("/admin/member-edit/<int:member_id>")
def memberEditPage(member_id):
    if memberIDValid(member_id) == True:
        
        connection = getCursor()
        connection.execute("SELECT members.MemberID, teams.TeamName, members.FirstName, members.LastName, members.City, members.Birthdate \
                           FROM members\
                           JOIN teams ON teams.TeamID = members.TeamID\
                           WHERE members.MemberID=%s;", (member_id,))
        memberInfo = connection.fetchall()

        nameMember = memberInfo[0][2] + ' ' + memberInfo[0][3]
    else:
        return render_template("404.html")
        
    return render_template("member_edit.html",namemember = nameMember,memberinfo = memberInfo, memberid = member_id)

@app.route("/admin/database_reset")
def databaseReset():
    return render_template("database_reset.html")


@app.route("/admin/database_reset/loading")
def databaseResetSQL():
    connection = getCursor()
    connection.execute("DROP TABLE IF EXISTS events, event_stage, event_stage_results, members, teams;")
    

    with app.open_resource('nzoly_structure_data_pa.sql', 'r') as sqlFile:
        sqlStatements = sqlFile.read()

    connection.execute(sqlStatements)
    
    return redirect(url_for('admin'))
