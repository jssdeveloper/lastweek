from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3" # Connects / Creates mysql3 database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)




####################################################################################
################################# DATABASE MODELS ##################################
####################################################################################

class Weather_search_log(db.Model): # Task 1 Main log, includes Task 3 - Record add/change/delete events
    id = db.Column(db.Integer, primary_key = True, nullable=False)
    log_event = db.Column(db.String)
    date = db.Column(db.String)
    time = db.Column(db.String)
    city = db.Column(db.String)
    temperature = db.Column(db.String)

class Log_last5(db.Model): # Task 2 -log last 5 searches
    id = db.Column(db.Integer, primary_key = True, nullable=False)
    city = db.Column(db.String, nullable = False)
    date = db.Column(db.String)
    temperature = db.Column(db.String)

class Cities_active(db.Model): # Task 3 route /cities - cities of interest
    id = db.Column(db.Integer, primary_key = True, nullable=False)
    city = db.Column(db.String, nullable = False)
    temperature = db.Column(db.String) # store weather data for list item
    ## Weather data will be pulled on get request from weather api

class Users(db.Model): # Identify by login
    id = db.Column(db.Integer, primary_key = True, nullable=False)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)

## CREATE DB AND TABLES
# with app.app_context():
#     db.create_all()




####################################################################################
##################################### ROUTES #######################################
####################################################################################


##--------------------------------- HOME ROUTE -----------------------------------##
## ------------------------------------------------------------------------------ ##
@app.route("/") # Home greeting page
def home_route():
    return render_template("home.html")



##------------------------------ LAST 5 SEARCHES LOG -----------------------------##
## ------------------------------------------------------------------------------ ##
@app.route("/log") # Display log of last 5 searches
def last_5_log_route():
    return render_template("last5.html")



###################################### CITIES ######################################
@app.route("/cities") # Display main app with weather cards
def cities_of_interest_route():
    return render_template("cities.html")



#################################### EVENT LOG #####################################
@app.route("/eventlog") # Log with all history and record add/change/delete events
def eventlog_all_route():
    with app.app_context():
        usrquery = Weather_search_log.query.all()
    return render_template("eventlog.html", usrquery=usrquery)



################################### ADMIN PANEL ####################################
@app.route("/admin", methods = ["GET","POST"]) # Admin panel with registrated users
def admin_route():
    with app.app_context():
        usrquery = Users.query.all()
    return render_template("admin.html", usrquery=usrquery)


## ADD USER ##
@app.route("/adduser",methods=["POST"])
def add_user():
    form_username = request.form.get("form_username")
    form_password = request.form.get("form_password")
    with app.app_context():
        adduser = Users(username=form_username, password=form_password)
        log = Weather_search_log(log_event = "Added User", date = datetime.now().strftime("%d/%m/%Y"), time = datetime.now().strftime("%H:%M:%S"), city = adduser.username)
        db.session.add(log)
        db.session.add(adduser)
        db.session.commit()
    return redirect(url_for("admin_route"))


    # log_event = db.Column(db.String)
    # date = db.Column(db.String)
    # time = db.Column(db.String)
    # city = db.Column(db.String)
    # temperature = db.Column(db.String)

## REMOVE USER ##
@app.route("/removeuser/<int:user_id>",methods=["POST","GET"])
def remove_user(user_id):
    with app.app_context():
        user_to_remove = Users.query.filter_by(id=user_id).first()
        log = Weather_search_log(log_event = "Removed User", date = datetime.now().strftime("%d/%m/%Y"), time = datetime.now().strftime("%H:%M:%S"), city = user_to_remove.username)
        db.session.add(log)
        db.session.delete(user_to_remove)
        db.session.commit()
    return redirect(url_for("admin_route"))




###################################### LOGIN #######################################
@app.route("/login") # Login route
def login_route():
    return render_template("login.html")

