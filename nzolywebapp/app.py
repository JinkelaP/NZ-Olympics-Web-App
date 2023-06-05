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
        
# date convert function, but actually also convert tuples to lists

def dateConvert(mySQLConnect, x):
    while type(mySQLConnect[0]) == tuple:
        listTupleInfo = list(mySQLConnect[0])
        if type(x) == int:
            listTupleInfo[x] = listTupleInfo[x].strftime("%d/%m/%Y")
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
            dateConvert(upcomingList,2)
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
            dateConvert(previousListFull,2)
      
        # convert positions to medals or qualifying status
        for memberResult in previousListFull:
            if memberResult[5] == 3:
                memberResult[5] = 'Bronze'
            elif memberResult[5] == 2:
                memberResult[5] = 'Silver'
            elif memberResult[5] == 1:
                memberResult[5] = 'Gold'
            elif memberResult[5] == None:

                memberPoints = memberResult[6]
                connection.execute(f'SELECT event_stage.PointsToQualify FROM event_stage \
                                    WHERE event_stage.StageID = {memberResult[7]};')
                qualiPoints = connection.fetchall()[0][0]
                
                if type(memberPoints) is float and type(qualiPoints) is float:
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


@app.route("/admin/Edit")
def edit():
    connection = getCursor()

    connection.execute("SELECT members.memberID, teams.TeamName, members.FirstName, members.LastName, members.City, members.Birthdate FROM members \
                JOIN teams ON teams.TeamID = members.TeamID;")
    searchResult1 = connection.fetchall()

    dateConvert(searchResult1,5)

    if searchResult1 == []:
        searchResult1 = None

    connection.execute("SELECT events.EventID, events.EventName, events.Sport, teams.TeamName FROM events \
                JOIN teams ON teams.TeamID = events.NZTeam;")
    searchResult2 = connection.fetchall()

    if searchResult2 == []:
        searchResult2 = None

    connection.execute("SELECT event_stage.StageID, events.EventName, event_stage.StageName, event_stage.StageDate, event_stage.Location, \
                        event_stage.PointsToQualify FROM event_stage \
                        JOIN events ON events.EventID = event_stage.EventID;")
    searchResult3 = connection.fetchall()

    if searchResult3 == []:
        searchResult3 = None
    else:
        dateConvert(searchResult3,3)
    
    for memberResult in searchResult3:
            if memberResult[5] == None:
                memberResult[5] = 'N/A'

    connection.execute("SELECT event_stage_results.ResultID, events.EventName, event_stage.StageName, members.FirstName, \
                       event_stage_results.PointsScored, event_stage_results.Position, event_stage_results.StageID\
                        FROM event_stage_results\
                        JOIN event_stage ON event_stage.StageID=event_stage_results.StageID\
                        JOIN members ON members.MemberID=event_stage_results.MemberID\
                        JOIN events ON events.EventID = event_stage.EventID;")
    searchResult4 = connection.fetchall()

    dateConvert(searchResult4,None)

    if searchResult4 == []:
        searchResult4 = None
    
    for memberResult in searchResult4:

            if memberResult[5] == 3:
                memberResult[5] = 'Bronze'
            elif memberResult[5] == 2:
                memberResult[5] = 'Silver'
            elif memberResult[5] == 1:
                memberResult[5] = 'Gold'

            elif memberResult[5] == None:
                memberPoints = memberResult[4]
                connection.execute(f'SELECT event_stage.PointsToQualify FROM event_stage \
                                    WHERE event_stage.StageID = {memberResult[6]};')
                qualiPoints = connection.fetchall()[0][0]
                
                if type(memberPoints) is float and type(qualiPoints) is float:
                    if memberPoints >= qualiPoints:
                        memberResult[5] = 'Qualified'
                    else:
                        memberResult[5] = 'Not Qualified'
                else:
                    memberResult[5] = 'N/A'

    for list in searchResult4:
            del list[-1:]
    
    connection.execute("SELECT * FROM teams;")
    teamList = connection.fetchall()

    return render_template("edit.html",searchresult1 = searchResult1, searchresult2 = searchResult2, searchresult3 = searchResult3, searchresult4 = searchResult4, teamlist = teamList)

@app.route("/admin/save_changes_member", methods=['POST'])
def saveChangesMember():
    memberID = request.form.get('memberid')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    city = request.form.get('city')
    birthDate = request.form.get('date')
    teamID = request.form.get("teams")

    connection = getCursor()
    connection.execute("UPDATE members \
                       SET TeamID = %s, FirstName = %s, LastName = %s, City = %s, Birthdate = %s\
                       WHERE MemberID = %s;",(teamID,firstName,lastName,city,birthDate,memberID))

    return redirect("/admin/Edit")

@app.route("/admin/add_member", methods=['POST'])
def addMember():
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    city = request.form.get('city')
    birthDate = request.form.get('date')
    teamID = request.form.get("teams")

    connection = getCursor()
    connection.execute("INSERT INTO members \
                       (teamID, FirstName, LastName, City, Birthdate)\
                       VALUES (%s, %s, %s, %s, %s);",(teamID,firstName,lastName,city,birthDate))

    return redirect("/admin/Edit")

@app.route("/admin/medals")
def showMedals():
    pass

@app.route("/admin/event_add", methods=['POST'])
def addEvent():
    eventName = request.form.get('eventName')
    sport = request.form.get('sport')
    teamID = request.form.get("teams")

    connection = getCursor()
    connection.execute("INSERT INTO events \
                       (EventName, Sport, NZTeam)\
                       VALUES (%s, %s, %s);",(eventName, sport, teamID))

    return redirect("/admin/Edit")

@app.route("/admin/event_stage_add")
def addEventStage():
    pass

@app.route("/admin/event_stage_results_add")
def addStageResults():
    pass