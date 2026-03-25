from server import reset_user_password, make_dev_user, password_check
from database_methods import DatabaseMethods
import os
print("Select a function:")
print("1 - Reset a password")
print("2 - Delete a user")
print("3 - Create a developer account")
print("4 - Create a new missions")

selection = int(input())

if selection == 1:
    #Developer method to update a user's password
    #IMPORTANT - Only use if requested to
    print("Input username:")
    uname = input()
    print("Enter user email:")
    email = input()
    print("Enter the new password:")
    newPass = input()
    if reset_user_password(uname, email, newPass):
        print("Password Updated")
    else:
        print("Please input a more secure password")
elif selection == 2:
    #Developer method to delete a user account
    #IMPORTANT - Only use if requested to or if user is malicious
    print("Input username:")
    uname = input()
    db = DatabaseMethods()
    id = db.getUserIDFromName(uname)[0]
    db.deleteUser(id)
    db.closeConnection()
    print("User Deleted")
elif selection == 3:
    #take the info for the new developer account
    print("Enter developer username:")
    uname = input()
    print("Enter developer email:")
    email = input()
    print("Enter developer password:")
    pwd = input()
    result = password_check(pwd)
    if result == 'PASSED':
        make_dev_user(uname, email, pwd)
    else:
        print(result)
elif selection == 4:
    db = DatabaseMethods()
    #db entry info
    print("Input question:")
    question = input()
    print("Input indicator (distance, greenery, lighting, crime, gradient):")
    indicator = input()
    print("Enter start node:")
    start = int(input())
    print("Enter end node:")
    end = int(input())
    print("Enter answer(Red, Green, Blue):")
    answer = input()
    print("Enter mission tier(1,2,3):")
    tier = int(input())
    #image info
    print("Enter filepath of mission image (must be in png format):")
    fpath = input()

    #check validity of provided inputs
    valid = os.path.exists(fpath) and fpath.lower().endswith('.png','.png"') and ["Red", "Green", "Blue"].__contains__(answer) and [1,2,3].__contains__(tier)

    if valid:
        id = db.addMission(question, indicator, start, end, answer, tier)
    else:
        print("Please make sure that your mission has the correct information.")
    
    db.closeConnection()
else:
    print("Invalid selection")
