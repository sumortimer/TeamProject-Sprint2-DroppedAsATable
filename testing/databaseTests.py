import unittest
import os
from database_methods import *

class TestDatabaseMethods(unittest.TestCase):
    # USER TESTS
    def testAddUser(self):
        db=DatabaseMethods()
        db.addUser("abc","abc@email.com","verysecurepassword123","T")
        users=db.getAllUsers()
        self.assertEqual(users,[(1,),(2,),(3,)])
        db.closeConnection()
        resetDatabase()

    def testUserType(self):
        db = DatabaseMethods()
        userType = db.getUserType(1)
        self.assertEqual(userType[0][0], "T") # note that single values are returned as tuples
        userType = db.getUserTypeViaUsername("test2")
        self.assertEqual(userType, [("A",)])
        db.closeConnection()
        resetDatabase()

    def testChangeUserType(self):
        db = DatabaseMethods()
        db.changeUserType("test2", "T")
        userType = db.getUserTypeViaUsername("test")
        self.assertEqual(userType, [("T",)])
        db.closeConnection()
        resetDatabase()

    def testUserWeights(self):
        db = DatabaseMethods()
        weights = db.getUserWeights(1)
        self.assertEqual(weights, [(1.0, 1.0, 1.0, 1.0, 1.0)])
        db.setUserWeights(1, [0,0.2,0.3,0.4,0.8])
        weights = db.getUserWeights(1)
        self.assertEqual(weights, [(0,0.2,0.3,0.4,0.8)])
        db.closeConnection()
        resetDatabase()

    def testAddPoints(self):
        db = DatabaseMethods()
        db.addPoints(1)
        points = db.getUserPoints(1)
        self.assertEqual(points, [(1,)])
        db.closeConnection()
        resetDatabase()

    def testDeleteUser(self):
        db = DatabaseMethods()
        db.deleteUser(1)
        users = db.getAllUsers()
        self.assertEqual(users, [(2,)])
        db.closeConnection()
        resetDatabase()

    def testAreUserDetailsUsed(self):
        db = DatabaseMethods()
        used = db.areUserDetailsUsed("test", "test@email.com")
        self.assertTrue(used)
        used = db.areUserDetailsUsed("Unique", "newperson@email.com")
        self.assertFalse(used)
        db.closeConnection()
        resetDatabase()

    # MAP TESTS
    def testGetIndicatorData(self):
        db = DatabaseMethods()
        nodes = db.getIndicatorData("lighting")
        self.assertEqual(nodes, [(1,0.1),(2,0.2),(3,0.3), (4,0.4)])
        db.closeConnection()
        resetDatabase()

    def testGetNodes(self):
        db = DatabaseMethods()
        nodes = db.getAllNodes()
        self.assertEqual(nodes, [(1, 0.1, 0.1, 0.1, 0.1), (2, 0.2, 0.2, 0.2, 0.2), (3, 0.3, 0.3, 0.3, 0.3), (4, 0.4, 0.4, 0.4, 0.4)])
        self.assertTrue(db.nodeExists(1))
        self.assertFalse(db.nodeExists(17))
        db.closeConnection()
        resetDatabase()
        

    def testUpdateNode(self):
        db = DatabaseMethods()
        db.updateNode(1, 2, 2, 5, 5, 5, 5)
        nodes = db.getAllNodes()
        self.assertEqual(nodes[0], (1, 5, 5, 5, 5))
        db.closeConnection()
        resetDatabase()

    def testGetAllEdges(self):
        db = DatabaseMethods()
        edges = db.getAllEdges()
        self.assertEqual([(1, 1, 2, 20), (2, 1, 3, 40), (3, 2, 3, 50)], edges)
        db.closeConnection()
        resetDatabase()

    def testUpdateEdgeLength(self):
        db = DatabaseMethods()
        db.editLength(1, 30)
        edges = db.getAllEdges()
        self.assertEqual([(1, 1, 2, 30.0), (2, 1, 3, 40.0), (3, 2, 3, 50.0)], edges)
        db.closeConnection()
        resetDatabase()

    def testGetSurroundingLength(self):
        db = DatabaseMethods()
        oneEdges = db.getSurroundingLength(1)
        self.assertEqual(oneEdges, [(2, 20), (3, 40)])
        db.closeConnection()
        resetDatabase()

    def testDeleteNode(self):
        db = DatabaseMethods()
        db.deleteNode(1)
        self.assertFalse(db.nodeExists(1))
        edges = db.getAllEdges()
        self.assertEqual([(3, 2, 3, 50)], edges)
        self.assertEqual([(2, "St. David's")], db.getLocationList())
        db.closeConnection()
        resetDatabase()

    def testGetLocations(self):
        db = DatabaseMethods()
        locs = db.getLocationList()
        self.assertEqual(locs, [(1, "University of Exeter"), (2, "St. David's")])
        node = db.getNodeFromLocation("University of Exeter")
        self.assertEqual(node, 1)
        db.closeConnection()
        resetDatabase()

    def testUpdateLocation(self):
        db = DatabaseMethods()
        db.updateLocation(1, 3, "University of NotExeter", "University")
        locs = db.getLocationList()
        node = db.getNodeFromLocation("University of NotExeter")
        self.assertEqual(node, 3)
        self.assertEqual(locs, [(3, "University of NotExeter"),(2, "St. David's")])
        db.closeConnection()
        resetDatabase()

    # MISSION TESTS

    def testGetMissionData(self):
        db = DatabaseMethods()
        selectData = db.getMissionSelectData()
        self.assertEqual(selectData, [(1, "Choose the most well lit route")])
        data = db.getMissionData(1)
        self.assertEqual(data, [("lighting", 1, 4, "Red")])
        tier = db.getMissionTier(1)
        self.assertEqual(tier, [(1, "Choose the most well lit route", "Red")])
        db.closeConnection()
        resetDatabase()

    def testEditMission(self):
        db = DatabaseMethods()
        db.editMission(1, 1, "Choose the most green route", "greenery", 2, 3,"Green","2")
        selectData = db.getMissionSelectData()
        self.assertEqual(selectData, [(1, "Choose the most green route")])
        data = db.getMissionData(1)
        self.assertEqual(data, [("greenery", 2, 3,"Green")])
        log = db.getLog()
        self.assertEqual((log[0][0], log[0][1], log[0][2]), (1,1,1))
        db.closeConnection()
        resetDatabase()

    def testEditIndicators(self):
        db = DatabaseMethods()
        db.editIndicators(1, 0.2, 0.2, 0.2, 0.2)
        nodes = db.getIndicatorData("lighting")
        self.assertEqual(nodes, [(1,0.2),(2,0.2),(3,0.3), (4,0.4)])
        db.closeConnection()
        resetDatabase()
        
    
def resetDatabase():
    try:
        os.remove("test_database.db")
    except:
        pass
    db = DatabaseMethods()
    #nodes
    db.addNode(1, 1, 0.1, 0.1, 0.1, 0.1, 0.1)
    db.addNode(2, 2, 0.2, 0.2, 0.2, 0.2, 0.2)
    db.addNode(3, 3, 0.3, 0.3, 0.3, 0.3, 0.3)
    db.addNode(4, 4, 0.4, 0.4, 0.4, 0.4, 0.4)
    #edges
    db.addEdge(1, 1, 2, 20.0)
    db.addEdge(2, 1, 3, 40.0)
    db.addEdge(3, 2, 3, 50.0)
    #user
    db.addUser("test", "test@email.com", "password", "T")
    db.addUser("test2", "test2@email.com", "password2", "A")
    #location
    db.addLocation(1,1,"University of Exeter", "University")
    db.addLocation(2,2,"St. David's", "Station")
    #missions
    db.addMission("Choose the most well lit route", "lighting", 1, 4,"Red",1)
    db.closeConnection()
    

if __name__ == '__main__':
    resetDatabase()
    unittest.main(exit=False)
    os.remove("test_database.db")
