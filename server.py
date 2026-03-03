from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
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

                # Checks if a username and password has actually been sent.
                if (not username or not password):
                    return render_template("login.html", error="No username or password has been entered")

                # Checks if a non-blank username and password has actually been sent.
                if username == "" or password == "":
                    return render_template("login.html", error="No username or password has been entered")
                

                # Checks with the database to see if a user with this username exists.
                database_response = myDatabase.getLoginDetails(username)
                print(database_response[0][0])

                # Checks if the response is blank.
                if not database_response:
                    # Blanks response either means no user exists or bad database connection.
                    return render_template("login.html", error="Incorrect username or password has been entered")

                database_password = database_response[0][0]

                # If the passwords match then redirect the user to /map.
                if database_password == password:
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
    if request.method == "POST":
        # Check with database
        return render_template("signup.html")


@app.route("/missions_t1.html", methods=["GET"])
def missions_1r():
    return redirect(url_for('missions_1'))

@app.route("/missions_t1", methods=["GET"])
def missions_1():
    if request.method == "GET":
        myDatabase = DatabaseMethods()
        question1 = "Mission Description"
        id = 1
         
        try:
            database_response = myDatabase.getMissionQuestion(id)
            question1 = database_response[0][0]
        finally:
            myDatabase.closeConnection()
            return render_template("missions_t1.html", question1=question1)
    # elif request.method == "POST":
    #     data = request.get_json()
    #     print(data)
    #     # Get mission name and description from database using the mission id

    #     # Pass name and description through to the edit mission page



    #     print(url_for("edit_mission", id=data["number"]))
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
            id = request.args.get('id', type=int)


            # Checks if ID variable is actually in the URL.
            if id == None:
                return redirect(url_for("/missions_t1"))
            

            # Gets question from the URL.
            database_response = myDatabase.getMissionQuestion(id)

            print(database_response) # REMOVE PRINT
            if not database_response:
                return redirect(url_for("/missions_t1"))
            if database_response[0] == None:
                return redirect(url_for("/missions_t1"))
            
            question = database_response[0][0]
            print(question) # REMOVE PRINT

            return render_template("edit_mission.html", question=question)
        except Exception as e:
            return 500
        finally:
            myDatabase.closeConnection()

    elif request.method == "POST":
        myDatabase = DatabaseMethods()
        try:
            try:
                data = request.get_json()
                id = data["id"]
                question = data["question"]
            except Exception as e:
                id = None
                question = None

            print(f"ID: {id} \nQuestion: {question}") # REMOVE PRINT

            # Check to see if required arguments were sent
            if id == None or question == None:
                # Returns 400 BAD_REQUEST
                return 400
            
            print("Past the check") # REMOVE PRINT

            # [0][0] is focusIndicator, [0][1] is startNode, [0][1] is endNode
            database_response = myDatabase.getMissionData(id)

            print(f"Response: {database_response}") # REMOVE PRINT

            # No mission with this ID exists
            if not database_response:
                return 400


            # Change userID when implementing login system.
            # userID, missionID, newQuestion, focusIndicator, newStartNode,newEndNode
            print("editing mission") # REMOVE PRINT
            myDatabase.editMission(1, id, question, database_response[0][0], database_response[0][1], database_response[0][2])
            print("About to redirect") # REMOVE PRINT
            return redirect(url_for("/missions_t1"))
        
        except Exception as e:
            print("ERROR!")
            return 500
        
        finally:
            myDatabase.closeConnection()
    
        

@app.route("/user_profile.html", methods=["GET"])
def user_profiler():
    return redirect(url_for('/user_profile'))

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
            id = request.args.get('id', type=int)

            # Checks if ID variable is actually in the URL.
            if id == None:
                return redirect(url_for("missions_t1"))
            

            # Gets question from the URL.
            database_response = myDatabase.getMissionQuestion(id)

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
