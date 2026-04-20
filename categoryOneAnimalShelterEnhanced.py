"""
Blake Birch
Category 1 Enhancement
4-19-2026
"""
#Connections and ability for python to connect and work with MongoDB
from pymongo import MongoClient
from bson.objectid import ObjectId
import random #Built in Python random module for random number generate function
#Time use for MFA expiration capabilities for logon
import time
#Logging capabilities for tracking events in system
import logging
#Configuration of logging to print anything that is marked INFO or higher
logging.basicConfig(level=logging.INFO)
"""
Logging addition allows for system monitoring to keep records of what users were doing while 
accessing the system.
"""

#Multi-Factor Authentication Class

class MultiAuth:
    def __init__(self):
        self.users = {      
            # User dictionary to store username and password
            "admin" : "Pa$$w0rd"}
        #Store username with MFA code
        self.mfa_codes = {}
        #Store username with expiration time
        self.expiry = {}
        
    #If correct input, generates MFA code
    def login(self, username, password):
        #Verifies username and password matches
        if username in self.users and self.users[username] == password:
            #Create log showing successful user password authentication
            logging.info(f"User '{username}' password authenticated")
            code = str(random.randint(100000, 999999)) #6 digit authentication code
            #6 digit MFA code is stronger against brute force attacks

            #Saves code for user for later use
            self.mfa_codes[username] = code
            #Takes current time and begins 2 minute countdown for use of MFA code
            #This will boost security by not allowing replay attacks and limit brute force attack time
            self.expiry[username] = time.time() + 120

            #Display code on console(This is for testing purposes, real code would need to be sent via email)
            print(f"Simulated Code: {code}")

            #True is login step success and False if wrong credentials
            return True
        #Create log showing user failed login
        logging.warning(f"Login failed for user '{username}'")
        return False
    
    #Second step of authentication to check correct MFA code
    def verify_mfa(self, username, code):
        #Verifies that time has not been exceeded and if so code is expired and deleted preventing login
        if username in self.mfa_codes:
            if time.time() > self.expiry[username]:
                #Create log showing user code expired
                logging.warning(f"MFA expired for '{username}'")
                del self.mfa_codes[username]
                return False

        #Retrieves stored code for comparison
        if self.mfa_codes.get(username) == code:
            #Create log showing successful login
            logging.info(f"Verification success for '{username}'")
            #If successful deletes code for no reuse
            del self.mfa_codes[username]

            #True will confirm authentication and False denies access
            return True
        #Create log showing user had invalid login attempt
        logging.warning(f"Invalid MFA attempt for '{username}'")
        return False
"""
Creation of a servicing layer method that will handle what is allowed to happen with data manipulation in
the database. This concept is a stronger way of engineering the program allowing a layered approach to 
development ensuring that multiple layers are required to perform all the functions instead of one layer 
completing all the functions. This layer verifies input and user authorization which keeps these functions out
of the database layer so that it can work the data itself. It also is a separate layer from the MFA layer so 
that the MFA layer can solely work on user access.
"""
class AnimalService:
    def __init__(self, shelter):
        self.shelter = shelter
    #Creation validation to ensure input is valid
    def create_animal(self, data):
        if "name" not in data or "animal_type" not in data:
            raise ValueError("Missing required information")
        #Call to database layer
        return self.shelter.create(data)
    #Read call with limit requirements to ensure excess data is not retrieved
    def get_animals(self, searchData=None):
        return self.shelter.read(searchData, limit=100)
    #Update call
    def update_animal(self, searchData, updateData):
        return self.shelter.update(searchData, updateData)
    #Delete call
    def delete_animal(self, deleteData):
        return self.shelter.delete(deleteData)

#Database Class

class AnimalShelter(object):
    """ Enhanced CRUD operations for Animal collection in MongoDB """

    def __init__(self, USER, PASS):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the 
        # animals collection, and the aac user.
        # Definitions of the connection string variables are
        # unique to the individual Apporto environment.
        #USER = 'aacuser'
        #PASS = '1234SnHu'

        #This information was to connect to the database
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 31382
        DB = 'AAC'
        COL = 'animals'
        #
        # Initialize Connection
        #
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]
        print ("Connection Successful")

# Create method
    def create(self, data):

        #Ensure data is not missing
        if not data:
            #Create log showing invalid input
            logging.error("Creation failed: Nothing to create") 
            raise ValueError("No data to create")

        #Inserts an item into database
        result = self.collection.insert_one(data)
        #Create log showing successful creation
        logging.info(f"Create operation executed. Created ID: {result.inserted_id}")
        return result.inserted_id

# Read Method
    def read(self, searchData = None, sort_field = None, limit = 0):
        """
        These new additions show defensive programming and awareness of malformed input
        throught input validation ensuring user inputs correct data. The logging errors
        create logs showing what was entered incorrectly for debugging and monitoring
        """
        if searchData is not None and not isinstance (searchData, dict):
            logging.error("Read failed: search_data not dictionary")
            raise ValueError("search_data must be a dictionary")
        if sort_field is not None and not isinstance(sort_field, str):
            logging.error("Read failed: sort_field not string")
            raise ValueError("sort_field must be a string")
        if not isinstance(limit, int) or limit < 0:
            logging.error("Read failed: limit not positive integer")
            raise ValueError("Limit must be a positive integer")
        
        #Retrieves data from database based on filter or returns all if no filter
        cursor = self.collection.find(searchData or {})

        #Allows sorting based on a field such as age, improvement to allow sorting of data for users
        if sort_field:
            cursor = cursor.sort(sort_field)

        #Applies limits to returns of searched results, improvement to allow more efficiency and less memory use
        if limit > 0:
            cursor = cursor.limit(limit)
        #Create log showing successful reads and result size
        results = list(cursor)
        logging.info(f"Read operation with filter: {searchData}, Results: {len(results)}")
        
        #Returns data into list
        return list(cursor)

# Update method
    def update(self, searchData, updateData):

        #Error thrown based on input not being found
        if not searchData:
            raise ValueError("No value found to update")
        if not updateData:
            raise ValueError("No update information to use")
        
        #Updates data that matches input, updates all matching documents with found specified fields
        result = self.collection.update_many(searchData, {"$set": updateData})

        #Improved user output to view number of data that matched and/or was modified
        return {
            "success": result.modified_count > 0,
            "modified": result.modified_count
        }

# Delete method
    def delete(self, deleteData):

       #Exception thrown if no data found from input
       if not deleteData:
           raise ValueError("No data found")

       #Deletes on item in database if matched with input
       result = self.collection.delete_one(deleteData)

       #Improved user information displaying number of items deleted
       return {
           "deleted": result.deleted_count
       }

#Main Program Flow

if __name__ == "__main__":
    # If using MongoDB login credentials
    # USER = "BBirch"
    # PASS = "SNHU2026"

    #Create instance to multiAuth class
    auth = MultiAuth()

    #Output prompts for username and password
    username = input("Username: ")
    password = input("Password: ")

    #Verification of username and password and prompts for MFA code if valid
    if auth.login(username, password):
        code = input("Enter code: ")

        #Ensures entered code matches stored code and if valid connects to AnimalShelter Class
        if auth.verify_mfa(username, code):
            print("Granted\n")

            #Credentials for admin level layer access capabilities
            USER = "yourUser"
            PASS = "yourPass"

            db = AnimalShelter(USER, PASS)
            shelter = AnimalService(db)

            #Example create information
            animal = {
                "name": "Ellie",
                "animal_type": "Lab"
            }

            created_id = shelter.create_animal(animal)
            print(f"Created animal ID: {created_id}")

        #Denies access if code does not match stored code
        else:
            print("Denied")

    #Output for unmatching username or password
    else:
        print("Invalid username or password")
