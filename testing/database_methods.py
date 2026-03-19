import sqlite3
import datetime

class DatabaseMethods:
    def __init__(self):
        self.connection=sqlite3.connect("test_database.db") #when the object is created, it either connects to, (or creates if not detected) task6.db
        self.connection.execute("PRAGMA foreign_keys = ON;") #enables foreign key constraints
        self.setup()

    # Destructor that automatically commits and closes the databases once the DatabaseMethods object goes out of scope.
    def __del__(self):
        try:
            self.connection.commit()
            self.connection.close()
        except:
            pass
            # Database is already closed.

    #call at the start, creates tables inside task6.db if they dont already exist
    def setup(self):
        try:
            cursor=self.connection.cursor()
        
            #table to store users, if anyone knows anything about password security stuff we could do that instead of storing plaintext
            cursor.execute("CREATE TABLE IF NOT EXISTS nodes(nodeID INTEGER PRIMARY KEY, coordinatesX REAL, coordinatesY REAL,lighting REAL, crime REAL, greenery REAL, gradient REAL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS users(userID INTEGER PRIMARY KEY, userName TEXT, email TEXT, password TEXT,userType TEXT CHECK(userType in ('T','A','M')), points INTEGER, lengthWeight REAL, lightingWeight REAL, crimeWeight REAL, greeneryWeight REAL, gradientWeight REAL)") # usertype enum is short for travellers, admins, maintainers as said in the spec
            cursor.execute("CREATE TABLE IF NOT EXISTS missions(missionID INTEGER PRIMARY KEY, question TEXT, focusIndicator TEXT CHECK(focusIndicator IN ('length','lighting','crime','greenery','gradient')), startNode INTEGER, endNode INTEGER, answer TEXT CHECK(answer IN ('Red','Green','Blue')), tier INTEGER, FOREIGN KEY(startNode) REFERENCES nodes(nodeID), FOREIGN KEY(endNode) REFERENCES nodes(nodeID))")
            cursor.execute("CREATE TABLE IF NOT EXISTS changes(changeID INTEGER PRIMARY KEY, userID INTEGER, missionID INTEGER, time TEXT, FOREIGN KEY(userID) REFERENCES users(userID), FOREIGN KEY(missionID) REFERENCES missions(missionID))")
            cursor.execute("CREATE TABLE IF NOT EXISTS locations(locationID INTEGER PRIMARY KEY, name TEXT, nodeID INTEGER, locationType TEXT, FOREIGN KEY(nodeID) REFERENCES nodes(nodeID))") #type will be used if we want to display locations with icons on the map e.g station type with a small train image etc...
            cursor.execute("CREATE TABLE IF NOT EXISTS edges(edgeID INTEGER PRIMARY KEY, startNode INTEGER, endNode INTEGER, length REAL, FOREIGN KEY(startNode) REFERENCES nodes(nodeID), FOREIGN KEY(endNode) REFERENCES nodes(nodeID))")
            cursor.execute("CREATE TABLE IF NOT EXISTS queryLog(queryID INTEGER PRIMARY KEY, userID INTEGER, startNode INTEGER, endNode INTEGER, overallWeight INTEGER, FOREIGN KEY(userID) REFERENCES users(userID),FOREIGN KEY(startNode) REFERENCES nodes(nodeID), FOREIGN KEY(endNode) REFERENCES nodes(nodeID))")
            self.connection.commit()
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")
    
    #methods used by route finding##
    def getUserWeights(self, userID):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT lengthWeight, lightingWeight, crimeWeight, greeneryWeight, gradientWeight FROM users WHERE userID = ?", (userID,))
            weights=cursor.fetchall()
            cursor.close()
            return(weights)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")
            
    def setUserWeights(self,userID, weights):
        try:
            cursor=self.connection.cursor()
            cursor.execute("UPDATE users SET lengthWeight=?, lightingWeight=?,crimeWeight=?, greeneryWeight=?, gradientWeight=? WHERE userID = ?",(weights[0],weights[1],weights[2],weights[3],weights[4],userID))
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getSurroundingLength(self,node):    #returns length of surrounding edges
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT startNode, length FROM edges WHERE endNode = ? UNION SELECT endNode, length FROM edges WHERE startNode = ?",(node,node))
            surroundingData=cursor.fetchall()
            cursor.close()
            return(surroundingData)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getPathCoordinates(self, path_nodes):
        coordinates = []
        cursor = self.connection.cursor()
        
        for node_id in path_nodes:
            cursor.execute("SELECT coordinatesX, coordinatesY FROM nodes WHERE nodeID = ?", (node_id,))
            result = cursor.fetchone()
            if result:
                coordinates.append([result[1], result[0]])  # [lat, lng]
        cursor.close()
        return coordinates

    def getAllNodes(self): 
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT nodeID, lighting, crime, greenery,gradient FROM nodes WHERE lighting IS NOT NULL")
            nodeIDs=cursor.fetchall()
            cursor.close()
            return(nodeIDs)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getAllEdges(self):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT * FROM edges WHERE length IS NOT NULL")
            allEdges=cursor.fetchall()
            cursor.close()
            return(allEdges)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getEdgeLength(self, start, end):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT length FROM edges WHERE (startNode = ? AND endNode =  ?) OR (startNode = ? AND endNode = ?)", (start, end, end, start))
            edge = cursor.fetchall()
            cursor.close()
            return(edge)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getScoreBreakdown(self, nodes):
        try:
            scores = []
            cursor = self.connection.cursor()
            for node_id in nodes:
                
                cursor.execute("SELECT lighting, crime, greenery, gradient FROM nodes WHERE nodeID = ?",(node_id,))
                result = cursor.fetchone()
                if result:
                    scores.append(result) # LCGG
            
            #find average scores
            ctr = 0
            lighting  = 0
            crime = 0
            greenery = 0
            gradient = 0
            for s in scores:
                ctr += 1
                lighting += s[0]
                crime += s[1]
                greenery += s[2]
                gradient += s[3]

            lighting = lighting / ctr
            crime = crime / ctr
            greenery = greenery / ctr
            gradient = gradient / ctr
            return [lighting, crime, greenery, gradient]
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")


    ################################

    #methods used by the map########
    def addNode(self,nodeID,coordinatesX,coordinatesY,lighting,crime,greenery,gradient):
        #try:
        cursor=self.connection.cursor()
        cursor.execute("INSERT INTO nodes (nodeID, coordinatesX, coordinatesY, lighting, crime, greenery, gradient) VALUES (?,?,?,?,?,?,?) ON CONFLICT(nodeID) DO UPDATE SET coordinatesX=excluded.coordinatesX, coordinatesY=excluded.coordinatesY, lighting=excluded.lighting, crime=excluded.crime, greenery=excluded.greenery, gradient=excluded.gradient", (nodeID, coordinatesX, coordinatesY, lighting, crime, greenery, gradient))
        self.connection.commit()
        cursor.close()
        #except(sqlite3.ProgrammingError):
            #print("Database connection has already been closed")

    def addPlaceholderNode(self, nodeID):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT OR IGNORE INTO nodes (nodeID, coordinatesX, coordinatesY, lighting, crime, greenery, gradient) VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL)", (nodeID,))
            self.connection.commit()
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    # Used to check if a node exists by the server script in order to create a dummy node if needed
    def nodeExists(self, nodeID):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM nodes WHERE nodeID = ? LIMIT 1", (nodeID,))
        exists = cursor.fetchone() is not None
        self.connection.commit()
        cursor.close()
        return exists

    def editIndicators(self, nodeID, lighting,crime,greenery,gradient): #used when editing the indicator values of a node
        try:
            cursor=self.connection.cursor()
            cursor.execute("UPDATE nodes SET lighting=?,crime=?,greenery=?,gradient=? WHERE nodeID=?",(lighting,crime,greenery,gradient,nodeID))
            self.connection.commit()
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed") 

    def addEdge(self,edgeID,startNode,endNode,length):
        try:
            cursor=self.connection.cursor()
            cursor.execute("INSERT INTO edges(edgeID,startNode,endNode,length) VALUES(?,?,?,?)",(edgeID,startNode,endNode,length))
            self.connection.commit()
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")
        

    def addLocation(self,nodeID,name,locationType):
        try:
            cursor=self.connection.cursor()
            cursor.execute("INSERT INTO locations (locationID,name,nodeID,locationType) VALUES(?,?,?,?)",(None,name,nodeID,locationType))
            self.connection.commit()
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def updateLocation(self, locationID, nodeID, name, locationType):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE locations SET nodeID=?, name=?, locationType=? WHERE locationID=?", (nodeID, name, locationType, locationID))
        self.connection.commit()
        cursor.close()

    def locationExists(self, locationID):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM locations WHERE locationID = ? LIMIT 1", (locationID,))
        exists = cursor.fetchone() is not None
        self.connection.commit()
        cursor.close()
        return exists

    # Used to update a placeholder node
    def updateNode(self, nodeID, coordinatesX, coordinatesY, lighting, crime, greenery, gradient):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE nodes SET coordinatesX=?, coordinatesY=?, lighting=?, crime=?, greenery=?, gradient=? WHERE nodeID=?", (coordinatesX, coordinatesY, lighting, crime, greenery, gradient, nodeID))
        self.connection.commit()
        cursor.close()

    def deleteNode(self, nodeID):  #deletes a node from the table using its nodeID, also removes any related edges and locations
        try:
            cursor=self.connection.cursor()
            cursor.execute("DELETE FROM locations WHERE nodeID =?",(nodeID,))
            cursor.execute("DELETE FROM edges WHERE startNode =?",(nodeID,))
            cursor.execute("DELETE FROM edges WHERE endNode =?",(nodeID,))
            cursor.execute("DELETE FROM changes WHERE missionID in (SELECT missionID FROM missions WHERE startNode=?)",(nodeID,))
            cursor.execute("DELETE FROM changes WHERE missionID in (SELECT missionID FROM missions WHERE endNode=?)",(nodeID,))
            cursor.execute("DELETE FROM missions WHERE startNode =?",(nodeID,))
            cursor.execute("DELETE FROM missions WHERE endNode =?",(nodeID,))
            cursor.execute("DELETE FROM queryLog WHERE startNode =?",(nodeID,))
            cursor.execute("DELETE FROM queryLog WHERE endNode =?",(nodeID,))
            cursor.execute("DELETE FROM nodes WHERE nodeID =?",(nodeID,))
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")


    ### REMEMBER TO ADD LOCATIONS ###
    def deleteEdgeByStartNode(self, startNode):
        try:
            cursor=self.connection.cursor()
            cursor.execute("DELETE FROM edges WHERE startNode =?", (startNode,))
            self.connection.commit()
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

  
    def getMapData(self): #returns a tuple containing (node/location data (if a node isnt a location, location data columns are null) and edge data not including placeholders
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT nodeID, coordinatesX, coordinatesY, lighting, crime, greenery, gradient FROM nodes WHERE lighting IS NOT NULL")
            nodesData = cursor.fetchall()
            cursor.execute("SELECT edgeID, startNode, endNode, length FROM edges WHERE length IS NOT NULL")
            edgeData = cursor.fetchall()
            cursor.execute("SELECT locationID, nodeID, name, locationType FROM locations")
            locationData = cursor.fetchall()
            cursor.close()
            return (nodesData, edgeData, locationData)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def editLength(self,edgeID,length):
        try:
            cursor=self.connection.cursor()
            cursor.execute("UPDATE edges SET length=? WHERE edgeID=?",(length,edgeID))
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed") 

    def getPlaceholderData(self): #returns the placeholder nodes and edges
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT nodes.nodeID FROM nodes  WHERE nodes.lighting IS NULL")
            nodesData=(cursor.fetchall())
            cursor.execute("SELECT edgeID, startNode, endNode FROM edges WHERE length IS NULL")
            edgeData=(cursor.fetchall())
            cursor.close()
            return(nodesData,edgeData)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getLocationList(self): #In case we want to have a menu to select start/end locations
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT nodeID, name FROM locations")
            locationList=cursor.fetchall()
            cursor.close()
            return(locationList)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getNodeFromLocation(self,name):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT nodeID FROM locations WHERE name=?",(name,))
            node=cursor.fetchall()
            cursor.close()
            return(node[0][0])
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getUserType(self, userID):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT userType from users WHERE userID=?",(userID,))
            type=cursor.fetchall()
            cursor.close()
            return(type)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")
    ################################

    #querylog methods###############
    def addQuery(self, userID, startNode, endNode, overallWeight): #adds a record of a route query to database, should be called every time the user searches for a route
        try:
            cursor=self.connection.cursor()
            cursor.execute("INSERT INTO queryLog (queryID, userID, startNode, endNode, overallWeight) VALUES (?,?,?,?,?)",(None, userID, startNode, endNode, overallWeight))
            cursor.close()
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getStartCount(self): #returns the name and count of locations sorted by how often they were chosen as a start location
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT name, COUNT(queryID) as noOcc FROM queryLog INNER JOIN locations on queryLog.startNode = locations.nodeID GROUP BY name")
            rates=cursor.fetchall()
            cursor.close()
            return(rates)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getEndCount(self): #returns the name and count of locations sorted by how often they were chosen as an end location
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT name, COUNT(queryID) as noOcc FROM queryLog INNER JOIN locations on queryLog.endNode = locations.nodeID GROUP BY name")
            rates=cursor.fetchall()
            cursor.close()
            return(rates)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getRouteCount(self):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT startNode, endNode, Count(queryID) as noOcc FROM queryLog GROUP BY startNode, endNode")
            routes=cursor.fetchall()
            cursor.close()
            return(routes)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")
            
    def getUserCount(self): #returns a list of users and query count sorted by the number of queries made
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT userName, COUNT(queryID) as noOcc FROM queryLog INNER JOIN users on queryLog.userID = users.userID GROUP BY userName ORDER BY noOcc DESC")
            rates=cursor.fetchall()
            cursor.close()
            return(rates)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getIndicatorData(self,indicator): #returns every nodeID and an indicator value for the input indicator
        try:
            if indicator not in ("lighting", "crime","greenery","gradient"):
                raise ValueError(f"Invalid indicator: {indicator}")
            else:
                cursor=self.connection.cursor()
                cursor.execute(f"SELECT nodeID, {indicator} FROM nodes")
                indicatorData=cursor.fetchall()
                cursor.close()
                return(indicatorData)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")
    ################################
    
    #mission methods################
    def addMission(self,question,focusIndicator, startNode,endNode, answer, tier):  #for use by an admin to add to the missions table
        try:
            cursor=self.connection.cursor()
            cursor.execute("INSERT INTO missions (missionID,question,focusIndicator,startNode,endNode, answer, tier) VALUES(?,?,?,?,?,?,?)",(None, question,focusIndicator, startNode,endNode, answer,tier))
            cursor.close()
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    def getMissionTier(self,tier):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT missionID, question, answer FROM missions WHERE tier =?",(tier,))
            tierMissions=cursor.fetchall()
            cursor.close()
            return(tierMissions)
        except(sqlite3.ProgrammingError):
            print("Database connection has already been closed")

    def getMissionSelectData(self):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT missionID, question from missions")
            missionSelectData=cursor.fetchall()
            cursor.close()
            return(missionSelectData)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    def getMissionQuestion(self, missionID):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT question from missions WHERE missionID =?", (missionID,))
            missionSelectData=cursor.fetchall()
            cursor.close()
            return(missionSelectData)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    def getMissionData(self, missionID):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT focusIndicator, startNode, endNode, answer from missions WHERE missionID =?",(missionID,))
            missionData=cursor.fetchall()
            cursor.close()
            return(missionData)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    def editMission(self,userID, missionID,newQuestion,newFocusIndicator, newStartNode,newEndNode,newAnswer,newTier):
        try:
            cursor=self.connection.cursor()
            cursor.execute("UPDATE missions SET question=?,focusIndicator=?,startNode=?,endNode=?, answer=?, tier=? WHERE missionID=?",(newQuestion,newFocusIndicator, newStartNode,newEndNode,newAnswer,newTier, missionID))
            cursor.execute("INSERT INTO changes (changeID, userID, missionID, time) VALUES(?,?,?,?)",(None,userID,missionID,int(datetime.datetime.now().timestamp())))
            cursor.close()
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    def editMissionQuestion(self, userID, missionID, newQuestion):
        try:
            cursor=self.connection.cursor()
            cursor.execute("UPDATE missions SET question=? WHERE missionID=?", (newQuestion, missionID))
            cursor.execute("INSERT INTO changes (changeID, userID, missionID, time) VALUES(?,?,?,?)", (None, userID, missionID, int(datetime.datetime.now().timestamp())))
            cursor.close()
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)
            
    def getLog(self):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT * FROM changes")
            changes=cursor.fetchall()
            cursor.close()
            return(changes)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)
            
    def addPoints(self, userID): #when a user completes a mission, use this to add a point to their score
        try:
            cursor=self.connection.cursor()
            cursor.execute("UPDATE users SET points = points + 1 WHERE userID = ?", (userID,))
            cursor.close()
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    def getUserPoints(self,userID):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT points FROM users WHERE userID = ?", (userID,))
            points=cursor.fetchall()
            cursor.close()
            return(points)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
    ################################

    #login and signup methods##################
    def addUser(self, username, email, password, usertype): # Used when a user chooses to sign up and make an account
        try:
            cursor=self.connection.cursor()
            cursor.execute("INSERT INTO users (userName, email, password, userType, points, lengthWeight, lightingWeight, crimeWeight, greeneryWeight, gradientWeight) VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (username, email, password, usertype, 0, 1, 1, 1, 1, 1))
            cursor.close()
            return True
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
            return False
        except Exception as e:
            print("Error: ", e)
            return False
        
    def getAllUsers(self): #for testing purposes
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT userID FROM users")
            users=cursor.fetchall()
            cursor.close()
            return(users)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        
    def deleteUser(self, userID): #removes a user from the database, ensures all dependent rows are deleted first
        try:
            cursor=self.connection.cursor()
            cursor.execute("DELETE FROM changes WHERE userID =?",(userID,))
            cursor.execute("DELETE FROM queryLog WHERE userID =?",(userID,))
            cursor.execute("DELETE FROM users WHERE userID =?",(userID,))
            cursor.close()
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")


    def getLoginDetails(self, username, email=None):  # Given the username and (optionally) the email, returns passwords. Also returns userID, which is used for other user related database methods.
        try:
            cursor=self.connection.cursor()

            if email is not None:
                cursor.execute("SELECT userID, password FROM users WHERE userName = ? AND email = ?", (username, email))
            else:
                cursor.execute("SELECT userID, password FROM users WHERE userName = ?", (username,))

            userDetails = cursor.fetchall()
            cursor.close()
            return(userDetails)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
            return []
        except Exception as e:
            print("Error: ", e)
            return []

    def areUserDetailsUsed(self, username, email): # Given username and email, are either already used in the account database?
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT userID FROM users WHERE userName = ? OR email = ?", (username, email))
            result = cursor.fetchall()
            cursor.close()

            # Returns true if either the username or email is used in the database.
            return len(result) > 0
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
            return True
        except Exception as e:
            print("Error: ", e)
            return True # Returns true in case of an error, to disallow duplicate entries in the event areUserDetailsUsed fails.

    # An alternative to getUserType that involves using a username instead
    def getUserTypeViaUsername(self, username):
        try:
            cursor=self.connection.cursor()
            cursor.execute("SELECT userType from users WHERE userName=?",(username,))
            type=cursor.fetchall()
            cursor.close()
            return(type)
        except sqlite3.ProgrammingError:
            print("Database connection has already been closed")
        except Exception as e:
            print("Error: ", e)

    #################################

    def closeConnection(self): # Please call this when you're finished
        self.connection.commit()
        self.connection.close()


