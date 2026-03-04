from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, re
from database_methods import *
import routefindingalgorithm

app = Flask(__name__)
#lighting, greenery, elevation, crime, distance
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start = request.form["start"]
        end = request.form["end"]

        return "Route saved to database!"

    return render_template("index.html")

@app.route("/map.html")
def map_redir():
    return redirect(url_for("index"))

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
    
    myDatabase.closeConnection()
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
    
    myDatabase.closeConnection()
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
    
    myDatabase.closeConnection()
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})
    
    
############ EDIT AND DELETE METHODS ###################

@app.route("/editnode", methods=["POST"])
def edit_node():
    data = request.get_json()
    myDatabase = DatabaseMethods()

    start_node = data["id"]
    myDatabase.deleteEdgeByStartNode(start_node)
    nodes, edges, locations = myDatabase.getMapData()
    myDatabase.closeConnection()
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
    myDatabase.closeConnection()
    
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

    myDatabase.closeConnection()
    
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
    myDatabase.closeConnection()
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

    myDatabase.closeConnection()
    
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
    myDatabase.closeConnection()
    return jsonify({"nodes": nodes, "edges": edges, "locations": locations})

############ Mission Methods ###################

@app.route("/login.html")
def login_redirect():
    return redirect(url_for('login'))
@app.route("/login", methods=["GET", "POST"])
def login():
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
                


                # # Usernames are case insensitive
                # username = username.lower()

                # Checks with the database to see if a user with this username exists.
                database_response = myDatabase.getLoginDetails(username)

                # Checks if the response is blank.
                if not database_response:
                    # Blanks response either means no user exists or bad database connection.
                    return render_template("login.html", error="Incorrect username or password has been entered")

                database_password = database_response[0][0]

                # If the passwords match then redirect the user to /map.
                if check_password_hash(database_password, password):
                    return redirect(url_for("index"))
                else:
                    return render_template("login.html", error="Incorrect username or password has been entered")
            except Exception as e:
                return render_template("login.html", error="Incorrect username or password has been entered")
            finally:
                myDatabase.closeConnection()


@app.route("/signup.html")
def signup_redirect():
    return redirect(url_for('signup'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
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
            myDatabase.addUser(username, email, generate_password_hash(password), usertype="A")

            # Validate the user's session.

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
    if request.method == "GET":
        myDatabase = DatabaseMethods()
        question1 = "Mission Description"
        mission_id = 1
         
        try:
            database_response = myDatabase.getMissionQuestion(mission_id)
            question1 = database_response[0][0]
        finally:
            myDatabase.closeConnection()
            return render_template("missions_t1.html", question1=question1)
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
    return render_template("missions_t2.html")


@app.route("/missions_t3.html", methods=["GET"])
def missions_3r():
    return redirect(url_for('missions_3'))

@app.route("/missions_t3", methods=["GET"])
def missions_3():
    return render_template("missions_t3.html")


@app.route("/edit_mission.html", methods=["GET"])
def edit_mission_r():
    return redirect(url_for("/edit_mission"))

@app.route("/edit_mission", methods=["GET", "POST"])
def edit_mission():
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


            # Check to see if required arguments were sent
            if mission_id == None or question == None:
                abort(400)

            database_response = myDatabase.getMissionData(mission_id)

            # No mission with this ID exists
            if not database_response:
                abort(400)


            # Change userID when implementing login system.
            myDatabase.editMission(1, mission_id, question, 
                                   database_response[0][0], # [0][0] is focusIndicator
                                   database_response[0][1], # [0][1] is startNode
                                   database_response[0][2]) # [0][2] is endNode
            return "missions_t1" # Not a redirect, as the frontend handles the redirect. Change it so backend handles redirect like with login?
        
        except Exception as e:
            return abort(500)
        
        finally:
            myDatabase.closeConnection()
    
        

@app.route("/user_profile.html", methods=["GET"])
def user_profiler():
    return redirect(url_for('user_profile'))

@app.route("/user_profile", methods=["GET"])
def user_profile():
    return render_template("user_profile.html")

@app.route("/mission_display.html", methods=["GET"])
def mission_display_r():
    return redirect(url_for("mission_display"))

@app.route("/mission_display", methods=["GET", "POST"])
def mission_display():
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

            return render_template("mission_display.html", question=question)
        except Exception as e:
            return redirect(url_for("missions_t1"))
        finally:
            myDatabase.closeConnection()

############ OTHER METHODS ###################

def ensure_node_exists(database, node_id):
    if not database.nodeExists(node_id):
        database.addPlaceholderNode(node_id)
   

if __name__ == "__main__":
    app.run(debug=False)
