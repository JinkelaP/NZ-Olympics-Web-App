# NZ-Olympics-Web-App

NZ-Olympics-Web-App web manage members, teams, events and stages in a local olympic committee. This is a school project.

## Structure

There are two main routes in the app, which are / and /admin.

### /

/ provides all public functions, including listmembers and listevents. When entering the url, python will connect to mySQL, fetching data from the database and rendering the page for users. 

For listmembers, it use a dynamic route to match GET request, which is the member id value assigned in the web page, to show the events that the member attended and will attend. The previous event function simply search the event_stage_results, however, the upcoming one not only search all events(stages) that the team of the member could participate, but also check if the member is qualified when a potential final stage is assigned to the team.

### /admin

/admin provides more advanced functions for the administrator of the Olympic Comittee only. The admin is able to add members, events, stages and results. The details of existing members are allowed to be editesIt shows a report of the memebers ordered by team, and a report of medals. A search function is also provided.

The add/edit page is designed in the same page. Though the page becomes long, the admin is able to jump to any part by clicking the button under the title of the page, so that the admin can finish all editing works without redirecting to another page. All editing forms are zoomed in a modal. Before submitting the form, it will check whether all inputs are validated. The submit via POST will be passed to python and mySQL query using parameterisation with %s in order to prevent injection attack. After submits, The page will be refreshed to the designated part of previous edit. The public will be able to see the changes in /.

## Assumptions

**Page Structure**

I create two base.html for all pages to inherit. The public one comes with grey navbar and buttons navigating to public pages. The admin one comes with blue navbar and buttons navigating to admin pages. In addition, the logo and title works on both base.html, and the botton is lighted up on the specific page.

**Request methods**

To be comprehensive, all 'search' requests are using GET, including listmembers/events and search bar(though it is actually a form) in the /admin. However, all add/edit requests are passed via POST, because the inputs from the form need to be validated first, keeping the security of the data and allowing bigger data size than GET.

**Data Storage**

Once the data is validated and passed to the back-end, a query of INSERT/UPDATE is used. Since the id of every table is auto increment, it is no need to worry about it. The primary keys and foreign keys keeps the data consistent across tables and allows convenient JOIN queries. Although the primary keys are required to be hidden by the assignment outline, I still show the primary keys of members and events in the search function, so that the member can search by ID, which is easier for managements sometimes.

**UI/UX**

The whole web app applys Bootstrap 5.3 for beautiful and unified UI design. Dangerous button are assigned by red, and edit buttons are yellow, which is warning in the Bootstrap language. The content of the page is included in a container so that it becomes flexible on different devices. The navbar is always shown on the top of the page to help user switch to other functions easily.

All add/edit forms are designed in a modal. If the inputed data is not valid, the form turns red with warning info in order to guide the user to correct the inputs.


## Discussion

The following developments should be made, if the app is going to support multiple different Olympics



Reference:
Olympics logo: https://olympics.com/ioc/olympic-rings