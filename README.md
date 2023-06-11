# NZ-Olympics-Web-App

# Intro
NZ-Olympics-Web-App web manage members, teams, events and stages in a local olympic committee. This is a school project.

# Structure

There are two main routes in the app, which are / and /admin.

## /

/ provides all public functions, including listmembers and listevents. When entering the url, python will connect to mySQL, fetching data from the database and rendering the page for users. 

For listmembers, it use a dynamic route to match GET request, which is the member id value assigned in the web page, to show the events that the member attended and will attend. The previous event function simply search the event_stage_results, however, the upcoming one not only search all events(stages) that the team of the member could participate, but also check if the member is qualified when a potential final stage is assigned to the team.

##/admin

/admin provides more advanced functions for the administrator of the Olympic Comittee only. The admin is able to add members, events, stages and results. The details of existing members are allowed to be editesIt shows a report of the memebers ordered by team, and a report of medals.

The add/edit page is designed in the same page. Though the page becomes long, the admin is able to jump to any part by clicking the button under the title of the page, so that the admin can finish all editing works without redirecting to another page. All editing forms are zoomed in a modal. Before submitting the form, it will check whether all inputs are validated. The submit via POST will be passed to python and mySQL query using parameterisation with %s in order to prevent injection attack. After submits, The page will be refreshed to the designated part of previous edit. The public will be able to see the changes in /.

# Assumptions

...

# Discussion

##The following developments should be made, if the app is going to support multiple different Olympics

...







Problem:

The women/men problem



Reference:
Olympics logo: https://olympics.com/ioc/olympic-rings