from flask import Flask, render_template, request, jsonify, redirect, url_for, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, re, os
from dotenv import load_dotenv
from database_methods import *
import routefindingalgorithm

app = Flask(__name__)

load_dotenv()
SESSION_KEY = os.environ.get("SESSION_KEY")
PEPPER_PASSWORD = os.environ.get("PEPPER_PASSWORD")

if not PEPPER_PASSWORD or not SESSION_KEY:
    raise ValueError("Missing required environment variables")

app.secret_key = SESSION_KEY

#lighting, greenery, elevation, crime, distance
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        start = request.form["start"]
        end = request.form["end"]

        return "Route saved to database!"
    
    # Sends user to login if they are not logged in
    if not isUserAuthenticated():
        return redirect(url_for("login"))

    if isUserAuthenticated(adminNeeded=True):
        return render_template("index.html", termsNeeded="False") # ADMIN CHANGE

    # If the user hasn't accepted the disclaimers this session then tell the index.html to pop-up the disclaimers.
    if not session.get("acceptedTerms"):
        session["acceptedTerms"] = True;
        return render_template("index.html", termsNeeded="True")

    return render_template("index.html", termsNeeded="False")

@app.route("/map.html")
def map_redir():
    return redirect(url_for("index"))

# Check for whether user is logged in or not
# If action requires the user to be an admin or above, then set adminNeeded, vice versa devNeeded.
# By default if app.debug is set to true then isUserAuthenticated is overridden for testing,
# you can override this to test this method while still remaining in debug by changing overrideDebug here to True.
def isUserAuthenticated(adminNeeded=False, devNeeded=False, overrideDebug=False):
    if app.debug and not overrideDebug:
        return True

    if adminNeeded:
        return bool(session.get("user_role") == "A" or session.get("user_role") == "M")
    elif devNeeded:
        return bool(session.get("user_role") == "M")
    return bool(session.get("user_name"))


############ Idea for custom error pages ###################
# @app.errorhandler(404)
# def page_not_found(e):
#     # e is the error object
#     return render_template('404.html'), 404


############ ADD METHODS ###################

@app.route("/addnode", methods=["POST"])
def add_node():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    node_id = data["id"]
    coordx = data["coordx"]
    coordy = data["coordy"]
    lighting = data["lighting"]
    crime = data["crime"]
    greenery = data["greenery"]
    gradient = data["gradient"]
    if myDatabase.nodeExists(node_id):
        print("Exists")
        myDatabase.updateNode(node_id, coordx, coordy, lighting, crime, greenery, gradient)
        
    else:
        print("Does not exist")
        myDatabase.addNode(node_id, coordx, coordy, lighting, crime, greenery, gradient)
            
    nodes, edges, locations = myDatabase.getMapData()
    
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})
    
@app.route("/addsegment", methods=["POST"])
def add_segment():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    segment_id = data["id"]
    start_node = data["startNode"]
    end_node = data["endNode"]
    length = data["length"]
    ensure_node_exists(myDatabase, start_node)
    ensure_node_exists(myDatabase, end_node)
    myDatabase.addEdge(segment_id, start_node, end_node, length)
    nodes, edges, locations = myDatabase.getMapData()
    
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})

@app.route("/addlocation", methods=["POST"])
def add_location():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    location_id = data["id"]
    name = data["name"]
    node_id = data["nodeID"]
    location_type = data["locationType"]

    if myDatabase.locationExists(location_id):
        print("Exists")
        myDatabase.updateLocation(location_id, node_id, name, location_type)
        
    else:
        print("Does not exist")
        myDatabase.addLocation(location_id, node_id, name, location_type)
            
    nodes, edges, locations = myDatabase.getMapData()
    
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})
    
    
############ EDIT AND DELETE METHODS ###################

@app.route("/editnode", methods=["POST"])
def edit_node():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    start_node = data["id"]
    myDatabase.deleteEdgeByStartNode(start_node)
    nodes, edges, locations = myDatabase.getMapData()
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})


@app.route("/editlocation", methods=["POST"])
def edit_location():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    name = data["name"]

@app.route("/editindicators", methods=["POST"])
def edit_indicators():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    node_id = data["id"]
    lighting = float(data["lighting"])
    crime = float(data["crime"])
    greenery = float(data["greenery"])
    gradient = float(data["gradient"])
    myDatabase.editIndicators(node_id, lighting, crime, greenery, gradient)
    nodes, edges, locations = myDatabase.getMapData()
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})

@app.route("/deletenode", methods=["POST"])
def delete_node():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    node_id = data["nodeID"]
    
    myDatabase.deleteNode(node_id)
    nodes, edges, locations = myDatabase.getMapData()
    myDatabase.closeConnection()
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})
    
############ GET METHODS ###################
                
@app.route("/getroute", methods=["POST"])
def get_route():
    data = request.get_json()
    start_node = int(data["startNode"])
    end_node = int(data["endNode"])
    weights = data["weights"]

    
    # Get data from database
    myDatabase = DatabaseMethods()
    myDatabase.setUserWeights(1, weights)
     
    
    # Find route
    myDatabase = DatabaseMethods()
    all_results = routefindingalgorithm.findMultipleRoutes((start_node, end_node))
    print(all_results)
    coordinates = myDatabase.getPathCoordinates(all_results[0])
    coordinatesTwo = myDatabase.getPathCoordinates(all_results[1])
    coordinatesThree = myDatabase.getPathCoordinates(all_results[2])

    #calculate distance of each route
    costOne = 0
    for i in range(0, len(all_results[0]) - 2):
        costOne += int(myDatabase.getEdgeLength(all_results[0][i], all_results[0][i + 1])[0][0])
    costTwo = 0
    for i in range(0, len(all_results[1]) - 2):
        costTwo += int(myDatabase.getEdgeLength(all_results[1][i], all_results[1][i + 1])[0][0])
    costThree = 0
    for i in range(0, len(all_results[2]) - 2):
        costThree += int(myDatabase.getEdgeLength(all_results[2][i], all_results[2][i + 1])[0][0])

    scoresOne = myDatabase.getScoreBreakdown(all_results[0])
    scoresTwo = myDatabase.getScoreBreakdown(all_results[1])
    scoresThree = myDatabase.getScoreBreakdown(all_results[2])

     
    
    return jsonify({
        "success": True,
        "path": all_results[0],
        "pathTwo": all_results[1],
        "pathThree": all_results[2],
        "coordinates": coordinates,
        "coordinatesTwo": coordinatesTwo,
        "coordinatesThree": coordinatesThree,
        "costOne": costOne,
        "costTwo": costTwo,
        "costThree": costThree,
        "scoreOne": scoresOne,
        "scoreTwo": scoresTwo,
        "scoreThree": scoresThree,
        "start": start_node,
        "end": end_node
    })

@app.route("/getroutefromname", methods=["POST"])
def get_route_from_name():
    myDatabase = DatabaseMethods()
    data = request.get_json()
    start_name = data.get("startName", "")
    end_name = data.get("endName", "")
    weights = data.get("weights")

    
    start_node = myDatabase.getNodeFromLocation(start_name)
    end_node = myDatabase.getNodeFromLocation(end_name)
    print(start_node)
    myDatabase.setUserWeights(1, weights)
     
    # Find route
    all_results = routefindingalgorithm.findMultipleRoutes((start_node, end_node))
    print(all_results)

    myDatabase = DatabaseMethods()
    
    coordinates = myDatabase.getPathCoordinates(all_results[0])
    coordinatesTwo = myDatabase.getPathCoordinates(all_results[1])
    coordinatesThree = myDatabase.getPathCoordinates(all_results[2])

    #calculate distance of each route
    costOne = 0
    for i in range(0, len(all_results[0]) - 2):
        costOne += int(myDatabase.getEdgeLength(all_results[0][i], all_results[0][i + 1])[0][0])
    costTwo = 0
    for i in range(0, len(all_results[1]) - 2):
        costTwo += int(myDatabase.getEdgeLength(all_results[1][i], all_results[1][i + 1])[0][0])
    costThree = 0
    for i in range(0, len(all_results[2]) - 2):
        costThree += int(myDatabase.getEdgeLength(all_results[2][i], all_results[2][i + 1])[0][0])

    scoresOne = myDatabase.getScoreBreakdown(all_results[0])
    scoresTwo = myDatabase.getScoreBreakdown(all_results[1])
    scoresThree = myDatabase.getScoreBreakdown(all_results[2])

     
    
    return jsonify({
        "success": True,
        "path": all_results[0],
        "pathTwo": all_results[1],
        "pathThree": all_results[2],
        "coordinates": coordinates,
        "coordinatesTwo": coordinatesTwo,
        "coordinatesThree": coordinatesThree,
        "costOne": costOne,
        "costTwo": costTwo,
        "costThree": costThree,
        "scoreOne": scoresOne,
        "scoreTwo": scoresTwo,
        "scoreThree": scoresThree,
        "start": start_node,
        "end": end_node
    })    

@app.route("/getmapdata", methods=["GET"])
def mapdata():
    myDatabase = DatabaseMethods()
    nodes, edges, locations = myDatabase.getMapData()
     
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})

############ Mission Methods ###################

@app.route("/login.html")
def login_redirect():
    return redirect(url_for('login'))
@app.route("/login", methods=["GET", "POST"])
def login():
    # Checks if user is authenticated, if they are then they are directed away from the log in page.
    if isUserAuthenticated():
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
            myDatabase = DatabaseMethods()
            try:
                username = request.form.get("username")
                password = request.form.get("password")   

                # Checks if a username and password have been sent and aren't blank.
                if (not username or not password):
                    return render_template("login.html", error="No username or password has been entered")

                # Usernames are case insensitive(?)
                # username = username.lower()

                # Checks with the database to see if a user with this username exists.
                database_response = myDatabase.getLoginDetails(username)
                #[0][0] = user_id, [0][1] = password

                # Checks if the response is blank.
                if not database_response:
                    # Blank response either means no user exists or bad database connection.
                    return render_template("login.html", error="Incorrect username or password has been entered")
                database_id = database_response[0][0]
                database_password = database_response[0][1]

                database_usertype = myDatabase.getUserType(database_id)
                if not database_usertype:
                    return render_template("login.html", error="Incorrect username or password has been entered")
                if not database_usertype[0]:
                    return render_template("login.html", error="Incorrect username or password has been entered")
                if not database_usertype[0][0]:
                    return render_template("login.html", error="Incorrect username or password has been entered")

                # If the passwords match then create session and redirect the user to /map.
                if check_password_hash(database_password, password + PEPPER_PASSWORD):

                    session["user_id"] = database_id
                    session["user_role"] = database_usertype[0][0]
                    session["user_name"] = username

                    return redirect(url_for("index"))
                else:
                    return render_template("login.html", error="Incorrect username or password has been entered")
            except Exception as e:
                return render_template("login.html", error=e)
            finally:
                myDatabase.closeConnection()


@app.route("/signup.html")
def signup_redirect():
    return redirect(url_for('signup'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Checks if user is authenticated, if they are then they are directed away from the sign up page.
    if isUserAuthenticated():
        return redirect(url_for("index"))

    if request.method == "GET":
            return render_template("signup.html")
    
    # If someone tries to register a new account:
    elif request.method == "POST":
        myDatabase = DatabaseMethods()
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password1")   
            password_confirm = request.form.get("password2")   

            # Are all fields present and non-empty in the request?
            if (not username or not email or not password or not password_confirm):
                return render_template("signup.html", error="Missing or empty inputs in signup request.")
            
            
            # Username(?) and email should be case-insensitive.
            # username = username.lower()
            email = email.lower()
            
            # Is the username or email already in use?
            if (myDatabase.areUserDetailsUsed(username, email)):
                return render_template("signup.html", error="Username or Email is already in use.")
            
            # USERNAME CHECKS

            # Is username below 5 characters?
            if (len(username) < 5):
                return render_template("signup.html", error="Username must be at least 5 characters long.")
            
            # Is username below 20 characters?
            if (len(username) > 20):
                return render_template("signup.html", error="Usernames cannot be longer than 20 characters.")
            
            # Does username only contain alphanumeric characters and underscores/hyphens (no spaces or special characters)?
            re_username_check = r"[\w-]+"
            if (not re.fullmatch(re_username_check, username)):
                return render_template("signup.html", error="Username should only contain alphanumeric characters or hyphens.")

            # Does username start with a number or special character?
            re_username_check = r"[A-Za-z][\w-]*"
            if (not re.fullmatch(re_username_check, username)):
                return render_template("signup.html", error="Username should not start with an underscore or hyphen.")

            # Should usernames be case-insensitive?


            # EMAIL CHECKS

            # Is the email invalid?
            re_email_valid = r"[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,20}"
                            # [a-zA-Z0-9._%+-]+ ensure one or more of specified characters, @ ensures mandatory at symbol, [A-Za-z0-9.-]+ one or more specificied characters in domain,
                            # \. ensures a mandatory ., [A-Za-z]{2,20} enforces a top-level domain (e.g., .com or .gov)
            
            if (not re.fullmatch(re_email_valid, email)):
                return render_template("signup.html", error="Invalid email.")


            # PASSWORD CHECKS

            # Are passwords equal?
            if (password != password_confirm):
                return render_template("signup.html", error="Passwords do not match.")
            
            # Is the password at least 8 characters?
            if (len(password) < 8):
                return render_template("signup.html", error="Password must be at least 8 characters.")

            # Is the password longer than 128 characters?
            if (len(password) > 128):
                return render_template("signup.html", error="Password cannot be longer than 128 characters.")

            # Does the password contain at least one uppercase letter, one lowercase letter, one digit, and one special character?
            re_pass_valid = r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^0-9A-Za-z])"
                            # (?=.*[A-Z]) checks for one upper case letter, (?=.*[a-z]) checks for one lowercase letter,
                            # (?=.*[0-9]) checks for one digit and (?=.*[^0-9A-Za-z]) checks for one special character.
            if (not re.match(re_pass_valid, password)):
                return render_template("signup.html", error="Password must contain at least one uppercase letter, one lower letter, one digit and a special character.")

            # Does the password contain any whitespace characters?
            re_pass_valid = r"(?=.*[\s])"
                            # (?=.*[\s]) checks for one whitespace character
            if (re.match(re_pass_valid, password)):
                return render_template("signup.html", error="Password must not contain any whitespace (such as characters).")

            # Does the password contain the username?
            re_pass_valid = re.escape(username.lower())
            if (re.search(re_pass_valid, password.lower())):
                return render_template("signup.html", error="Password must not contain the username.")


            # If everything is valid then sign the user up
            if (not myDatabase.addUser(username, email, generate_password_hash(password + PEPPER_PASSWORD), usertype="T")):
                return render_template("signup.html", error="Database error.")
            
            database_response = myDatabase.getLoginDetails(username)
            #[0][0] = user_id, [0][1] = password

            if not database_response:
                return render_template("signup.html", error="Database error.")
            
            user_id = database_response[0][0]

            # Validate the user's session.
            session["user_role"] = "T"
            session["user_name"] = username
            session["user_id"] = user_id

            return redirect(url_for("index"))

        except Exception as e:
            print("Error:", e)
            abort(500)
        finally:
            myDatabase.closeConnection()



@app.route("/missions_t1.html", methods=["GET"])
def missions_1r():
    return redirect(url_for('missions_1'))

@app.route("/missions_t1", methods=["GET"])
def missions_1():
    if not isUserAuthenticated():
        return redirect(url_for("index"))

    if request.method == "GET":
        myDatabase = DatabaseMethods()
        question1 = "Mission Description"
        ids = [1]
        missions = []
        for i in ids:
            database_response = myDatabase.getMissionQuestion(i)
            question = database_response[0][0]
            missions.append({
                'question': question,
                'id': i
            })
        myDatabase.closeConnection()

        if isUserAuthenticated(adminNeeded=True):
            return render_template("missions_t1.html", missions=missions) # ADMIN CHANGE
        
        return render_template("missions_t1.html", missions=missions)
    # elif request.method == "POST":
    #     data = request.get_json()
    #     print(data)
    #     # Get mission name and description from database using the mission id

    #     # Pass name and description through to the edit mission page



    #     print(url_for("edit_mission", mission_id=data["number"]))
    #     return redirect(url_for("edit_mission", id=data["number"]))
    #     # return redirect(f"/edit_mission.html?id={data["number"]}")


@app.route("/missions_t2.html", methods=["GET"])
def missions_2r():
    return redirect(url_for('missions_2'))

@app.route("/missions_t2", methods=["GET"])
def missions_2():
    if not isUserAuthenticated():
        return redirect(url_for("index"))
    
    if isUserAuthenticated(adminNeeded=True):
            return render_template("missions_t2.html") # ADMIN CHANGE
    return render_template("missions_t2.html")


@app.route("/missions_t3.html", methods=["GET"])
def missions_3r():
    return redirect(url_for('missions_3'))

@app.route("/missions_t3", methods=["GET"])
def missions_3():
    if not isUserAuthenticated():
        return redirect(url_for("index"))
    
    if isUserAuthenticated(adminNeeded=True):
            return render_template("missions_t3.html") # ADMIN CHANGE
    return render_template("missions_t3.html")


@app.route("/edit_mission.html", methods=["GET"])
def edit_mission_r():
    return redirect(url_for("edit_mission"))

@app.route("/edit_mission", methods=["GET", "POST"])
def edit_mission():
    if not isUserAuthenticated(adminNeeded=True):
        return redirect(url_for("index"))

    if request.method == "GET":
        myDatabase = DatabaseMethods()
        try:
            # Gets id from URL
            mission_id = request.args.get('id', type=int)


            # Checks if ID variable is actually in the URL.
            if mission_id == None:
                abort(404)
            

            # Gets question from the URL.
            database_response = myDatabase.getMissionQuestion(mission_id)

            if not database_response:
                abort(404)
            if database_response[0] == None:
                abort(404)
            
            question = database_response[0][0]

            return render_template("edit_mission.html", question=question)
        except Exception as e:
            abort(500)
        finally:
            myDatabase.closeConnection()

    elif request.method == "POST":
        myDatabase = DatabaseMethods()
        try:
            data = request.get_json(silent=True)
            if not data:
                abort(400)
            mission_id = data["id"]
            question = data["question"]


            # Checks to see if required arguments were sent
            if mission_id == None or question == None:
                abort(400)

            # No mission with this ID exists
            if not myDatabase.getMissionQuestion(mission_id):
                abort(400)

            if not session.get("user_id"): # DEBUG
                myDatabase.editMissionQuestion(-1, mission_id, question)
            else:
                myDatabase.editMissionQuestion(session["user_id"], mission_id, question)
            return "missions_t1" # Not a redirect, as the frontend handles the redirect. Change it so backend handles redirect like with login?
        
        except Exception as e:
            print("Error", e)
            abort(500)
        
        finally:
            myDatabase.closeConnection()
    
        

@app.route("/user_profile.html", methods=["GET"])
def user_profiler():
    return redirect(url_for('user_profile'))

@app.route("/user_profile", methods=["GET"])
def user_profile():
    if not isUserAuthenticated():
        return redirect(url_for("index"))
    return render_template("user_profile.html")

@app.route("/mission_display.html", methods=["GET"])
def mission_display_r():
    return redirect(url_for("mission_display"))

@app.route("/mission_display", methods=["GET", "POST"])
def mission_display():
    if not isUserAuthenticated():
        return redirect(url_for("index"))

    if request.method == "GET":
        myDatabase = DatabaseMethods()

        try:
            # Gets id from URL
            mission_id = request.args.get('id', type=int)

            # Checks if ID variable is actually in the URL.
            if mission_id == None:
                return redirect(url_for("missions_t1"))
            
            # Gets question from the URL.
            database_response = myDatabase.getMissionQuestion(mission_id)

            if not database_response:
                return redirect(url_for("missions_t1"))
            if database_response[0] == None:
                return redirect(url_for("missions_t1"))
            
            question = database_response[0][0]
            image = "mission_"+str(mission_id)+".png"
            # Check correct option here
            red = "Correct"
            green = "Incorrect"
            blue = "Incorrect"

            myDatabase.closeConnection()
            return render_template("mission_display.html", question=question, image=image, red=red, green=green, blue=blue)
        except:
            myDatabase.closeConnection()

# Needs to be tested
@app.route("/dev_panel", methods=["GET", "POST"])
def dev_panel():
    if not isUserAuthenticated(devNeeded=True):
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("dev_panel.html")
    
    # Everything below this is a POST method.
    myDatabase = DatabaseMethods()
    try:
        if "action" not in request.args:
            return render_template("dev_panel.html", error="Missing fields required")
        action = request.args.get("action", type=str)

        user_to_change = request.args.get('username', type=str)
        password_to_check = request.args.get('password', type=int)

        if not password_to_check or not user_to_change:
            return render_template("dev_panel.html", error="Missing fields required")
        
        # We should check if the dev entered their password correctly
        database_response = myDatabase.getLoginDetails(session.get("user_name"))

        if not database_response:
            return render_template("dev_panel.html", error="Database error")
        if not database_response[0]:
            return render_template("dev_panel.html", error="Database error")
        if not database_response[0][1]:
            return render_template("dev_panel.html", error="Database error")
        
        # Checks if the passwords don't match
        if not check_password_hash(database_response[0][1], password_to_check + PEPPER_PASSWORD):
            return render_template("dev_panel.html", error="Incorrect password")
        
        # Check if username exists, if they do then update them
        database_response = myDatabase.getUserTypeViaUsername(user_to_change)
        if not database_response:
            return render_template("dev_panel.html", error="Database error")
        if not database_response[0]:
            return render_template("dev_panel.html", error="Database error")
        if not database_response[0][0]:
            return render_template("dev_panel.html", error="Database error")
        
        user_type = database_response[0][0]

        new_user_type = ''
        if action == "promote":
            new_user_type = 'A'
        elif action == "demote":
            new_user_type = 'T'
        else:
            return render_template("dev_panel.html", error="Incorrect field entered")

        if user_type == "A" and action == "promote":
            return render_template("dev_panel.html", error="User is already admin")
        elif user_type == "T" and action == "demote":
            return render_template("dev_panel.html", error="User is already traveller")
        elif user_type == "M":
            return render_template("dev_panel.html", error="Cannot change permissions of developer")
        else:
            if (myDatabase.changeUserType(user_to_change, new_user_type)):
                correct = ""
                if action == "promote":
                    correct = "User promoted to admin"
                elif action == "demote":
                    correct = "User demoted to traveller"
                return render_template("dev_panel.html", correct=correct)
            return render_template("dev_panel.html", error="Database error promoting user")

    except Exception as e:
        print("Error: ", e)
        return render_template("dev_panel.html", error="Database error")
    finally:
        myDatabase.closeConnection()


# ADD LOG OUT METHOD


############ OTHER METHODS ###################

def ensure_node_exists(database, node_id):
    if not database.nodeExists(node_id):
        database.addPlaceholderNode(node_id)
   

if __name__ == "__main__":

    app.run(debug=True)
