from operator import itemgetter
import random

import numpy
import scipy

from database_methods import DatabaseMethods


def findRoute(segments, nodes, whereRouting, weightings=None):
    #apply weightings to segments to create a single final weight for each segment
    weightedSegments = []
    if weightings:
        for segment in segments: #apply weightings to each segment
            segmentid, start, end, length = segment
            weight = length * (weightings[0]**3) *2
            weightingIterator = 1
            for node in nodes:
                if node[0] == start:
                    for tempWeight in node[1:]:
                        weight += float(tempWeight)*(float(weightings[weightingIterator])**3)*length
                        weightingIterator+=1
            weightingIterator = 1
            for node in nodes:
                if node[0] == end:
                    for tempWeight in node[1:]:
                        weight += float(tempWeight)*(float(weightings[weightingIterator])**3)*length
                        weightingIterator+=1
            weightedSegments.append((start, end, weight))
    else:
        for segment in segments: #if no weighting only length is used
            segid, start, end, length = segment
            weight = length
            weightedSegments.append((start, end, weight))

    #create numpy matrix the size of the amount of nodes
    distmatrixSize = int(nodes[-1][0])
    distMatrix = numpy.zeros((len(nodes), len(nodes)))
    
    #add the segments to the numpy array
    for segment in weightedSegments:
        distMatrix[int(segment[0])][int(segment[1])] = segment[2]
        distMatrix[int(segment[1])][int(segment[0])] = segment[2]
    
    #use scipy dijkstras implementation to get distance and pred matrix
    distances, pred = scipy.sparse.csgraph.dijkstra(distMatrix, return_predecessors=True)

    return distances, pred






def findOtherRoutes(segments, nodes, whereRouting, routes, weightings = [1, 0, 0, 0, 0], seed = 0, similarityNeeded = 20, removingNodes = False):
    escapeCounter = 0 #escape counter to set max iterations so does not loop forever

    # calculate the total of weightings so that when the weights are adjusted it adjusts them by an apropriate amount
    weightingsMagnitude = 0
    for weight in weightings:
        weightingsMagnitude += weight


    while escapeCounter < 10:

        #randomise weightings to create the other routes
        weightings = []
        for x in range(5):
            weightings.append(random.uniform(0, weightingsMagnitude))
            seed+=1


        #start removing edges to force a different path
        if removingNodes == True:
            random.seed(seed)
            for singleRoute in routes:
                toRemove = random.choice(singleRoute)
                exitready = False
                while exitready == False:
                    for x in range(len(segments)):
                            if segments[x][1] == toRemove:
                                segments.pop(x)
                                break
                            if segments[x][2] == toRemove:
                                segments.pop(x)
                                break
                    exitready = True
                    seed+=1
                        
                    



        #attempt to find a different route with the new adjusted weightings 
        routeweights, routePr = findRoute(segments, nodes, whereRouting, weightings)
        route = (getPath(routePr,whereRouting[0], whereRouting[1]))
        isDifferent = True
        for firstRoute in routes:
            #similarity calculates what percentage of nodes the routes have in common
            similarity = len(set(route).difference(set(firstRoute)))/len(route) * 100
            
            #if the two routes are not different enough the weights will be adjusted again
            if similarity < similarityNeeded:
                isDifferent = False
        if isDifferent:
            return route, seed

        escapeCounter += 1
    return None, seed






#find multiple routes for the user to choose between
def findMultipleRoutes(whereRouting,userID = 1, numberOfRoutes = 3):

    #get data from the database
    myDatabase = DatabaseMethods()
    segments = myDatabase.getAllEdges()
    nodes = myDatabase.getAllNodes()
    weightingstemp = myDatabase.getUserWeights(userID)
    weightingstemp = weightingstemp[0]
    myDatabase.closeConnection()


    routes = []
    weightings = []

    largestWeight = 0
    for tempWeight in weightingstemp:
        if float(tempWeight) > largestWeight:
            largestWeight = float(tempWeight)
    for weightIterator in range(len(weightings)):
        weightings[weightIterator] = float(weightingstemp[weightIterator])/largestWeight
    firstRouteWeights, firstRoute = findRoute(segments, nodes, whereRouting, weightings)
    actualRoute = getPath(firstRoute, whereRouting[0], whereRouting[1])
    routes.append(actualRoute) # add first route to a list
    seed = int(whereRouting[0]+whereRouting[1]) # the seed is made to ensure that each time that the same 2 nodes are put in the same options are generated
    
    #find the correct number of different routes for the user to choose between
    iterator = 0
    while len(routes) < numberOfRoutes and iterator<3:
        newRoute, seed = findOtherRoutes(segments, nodes, whereRouting, routes, seed = seed)
        if newRoute:
            routes.append(newRoute)
        iterator += 1

    #start removing nodes to find more routes
    if len(routes) < numberOfRoutes:
        iterator = 0
        while len(routes) < numberOfRoutes and iterator<20:
            tempSegments = segments
            newRoute, seed = findOtherRoutes(tempSegments, nodes, whereRouting, routes, seed = seed, removingNodes = True)
            if newRoute:
                routes.append(newRoute)
            seed += 1
            iterator += 1


    while len(routes) < numberOfRoutes:
        routes.append(routes[0])
    return routes

#get the path from the priors matrix
def getPath(Pr,i,j):
    path = [int(j)]
    k = j
    while Pr[int(i)][int(k)]!= -9999:
        path.append(int(Pr[int(i)][int(k)]))
        k = Pr[int(i)][int(k)]
    return path[::-1]