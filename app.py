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
################################ UPDATE FUNCTION ###################################
####################################################################################

@app.route("/updateall")
def update_cities():
    from weatherapi import get_weather
    with app.app_context():
        saved_cities = Cities_active.query.all()
        for i in saved_cities:
            icity = (i.city)
            icity_id = (i.id)
            icity_weather = get_weather(icity)

            with app.app_context():
                new_weather = Cities_active.query.filter_by(id=icity_id).first()
                new_weather.temperature = icity_weather
                db.session.commit()
    return redirect(url_for("cities_of_interest_route"))
            


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
    with app.app_context():
        last_5_query = Log_last5.query.all()
    return render_template("last5.html",last_5_query=last_5_query)



###################################### CITIES ######################################
@app.route("/cities",methods = ["GET", "POST"]) # Display main app with weather cards
def cities_of_interest_route():

    with app.app_context():
        cityquery = Cities_active.query.all()
    return render_template("cities.html",cityquery=cityquery)



## SEARCH CITY ## to implement log
@app.route("/searchcity", methods = ["POST","GET"])
def search_city():
    city = request.form.get("form_search")
    from weatherapi import get_weather
    api_temp = get_weather(city)
    # Query saved cities
    with app.app_context():
        cityquery = Cities_active.query.all()
    # Log to main LOG
    with app.app_context():
        search_log = Weather_search_log(log_event = "Searched City", time = datetime.now().strftime("%H:%M:%S"), date = datetime.now().strftime("%d/%m/%Y"), city = city, temperature=api_temp)
        db.session.add(search_log)
        db.session.commit()
    # Log last 5
    with app.app_context():
        log_last_5 = Log_last5(date = datetime.now().strftime("%d/%m/%Y"), city = city, temperature=api_temp)
        db.session.add(log_last_5)
        db.session.commit()
    return render_template("cities.html",cityquery=cityquery,api_temp=str(api_temp),city=city)


## ADD CITY ## to implement log
@app.route("/addcity/<city>/<api_temp>",methods = ["POST","GET"])
def add_city(city,api_temp):
    with app.app_context():
        addcity = Cities_active(city=city, temperature=api_temp)
        db.session.add(addcity)
        db.session.commit()

    # ADD TO MAIN LOG
    with app.app_context():
        search_log = Weather_search_log(log_event = "Added city to favorites", time = datetime.now().strftime("%H:%M:%S"), date = datetime.now().strftime("%d/%m/%Y"), city = city, temperature=api_temp)
        db.session.add(search_log)
        db.session.commit()

    update_cities()
    return redirect(url_for("cities_of_interest_route"))



## REMOVE CITY ##
@app.route("/removecity/<city_id>",methods=["POST","GET"])
def remove_city(city_id):
    with app.app_context():
        city_to_remove = Cities_active.query.filter_by(id=city_id).first()
        db.session.delete(city_to_remove)
        search_log = Weather_search_log(log_event = "Deleted City", time = datetime.now().strftime("%H:%M:%S"), date = datetime.now().strftime("%d/%m/%Y"),city=city_to_remove.city)
        db.session.add(search_log)
        db.session.commit()
    update_cities()
    return redirect(url_for("cities_of_interest_route"))


## UPDATE CITY PAGE ##
@app.route("/update/<city_city>/<city_id>",methods=["POST","GET"])
def update_city_page(city_city,city_id):
    with app.app_context():
        search_log = Weather_search_log(log_event = "Favorite City Update Initiated", time = datetime.now().strftime("%H:%M:%S"), date = datetime.now().strftime("%d/%m/%Y"),city=city_city)
        db.session.add(search_log)
        db.session.commit()
    return render_template("update_city.html",city_city=city_city,city_id=city_id)


## UPDATE CITY FUNCTION ##
@app.route("/replacecity/<city_id>",methods=["POST","GET"])
def update_city_function(city_id):
    newcity = request.form.get("newcity")

    from weatherapi import get_weather
    newcity_weather = get_weather(newcity)

    with app.app_context():
        city_card_update = Cities_active.query.filter_by(id=city_id).first()
        city_card_update.city = newcity
        city_card_update.temperature = newcity_weather
        search_log = Weather_search_log(log_event = "Favorite City Updated", time = datetime.now().strftime("%H:%M:%S"), date = datetime.now().strftime("%d/%m/%Y"),city=newcity)
        db.session.add(search_log)
        db.session.commit()
    update_cities()

    return redirect(url_for("cities_of_interest_route"))


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


########################£############## FUN #############£##########################
@app.route("/fun")
def fun_route():
    gif_list = []
    city_list = []
    from gifapi import giphy

    with app.app_context():
        cityquery = Cities_active.query.all()
        for i in cityquery:
            gif_list.append(giphy(i.city))
            city_list.append(i.city)
    return render_template("fun.html",gif_list=gif_list,city_list=city_list)


###################################### LOGIN #######################################
@app.route("/login") # Login route
def login_route():
    return render_template("login.html")

