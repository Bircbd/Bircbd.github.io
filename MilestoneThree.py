# Imports a SQL database library
import sqlite3
# Keeping MongoDB access for multiple database usage
#from pymongo import MongoClient
#from bson.objectid import ObjectId

# Creation of class that will hold CRUD operations that will be used for both MongoDB and SQL databases
class AnimalShelter(object):
    # Constructor creation that adds ability for user to choose between MongoDB or SQLite based on db parameter
    def __init__(self, USER = None, PASS = None, db_type = "mongo"):
        #USER = 'aacuser'
        #PASS = '1234SnHu'
        # Storing of chosen database option
        self.db_type = db_type

        # Logic for choosing MongoDB and the login requirements to connect to database
        if self.db_type == "mongo":
            HOST = 'nv-desktop-services.apporto.com'
            PORT = 31382
            DB = 'AAC'
            COL = 'animals'
        # Initialize Connection
            self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
            self.database = self.client['%s' % (DB)]
            self.collection = self.database['%s' % (COL)]
            print ("Connection Successful")

        # Enhancement logic to access SQL database path
        elif self.db_type == "sql":
            # Creates SQL database file
            self.connection = sqlite3.connect("animals.db")
            # Cursor object to execute SQL commands and is used with connection
            self.cursor = self.connection.cursor()
            
            #Resets tables if they exist for testing functionality
            self.cursor.execute("DROP TABLE IF EXISTS animals")
            self.cursor.execute("DROP TABLE IF EXISTS breeds")
            self.cursor.execute("DROP TABLE IF EXISTS diets")

            #Creation of new lookup diet table
            #This table stores unique values to be referenced by an ID from the animals table
            #This will help to ensure that redundant variables are not stored repeatedly for better efficiency
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS diets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                diet_name TEXT UNIQUE
            )
            """)
            #Creation of new lookup breed table
            #This table stores unique values to be referenced by an ID from the animals table
            #This will help to ensure that redundant variables are not stored repeatedly for better efficiency
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS breeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                breed_name TEXT UNIQUE,
                diet_id INTEGER
            )
            """)

            # Creation of animal table
            # Creation of unique ID numbers for each record and defining of structured columns
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                breed_id INTEGER,
                diet_id INTEGER,
                age INTEGER
            )
            """)
            # Saving of changes as SQL does not automatically save
            self.connection.commit()

            print("Successful Connection to SQLite")
    # Diet query ability that will check for existing diet information and 
    # if there is none found, insert new information into database
    def use_diet(self, diet_name):
        self.cursor.execute(
            "SELECT id FROM diets WHERE diet_name = ?",
            (diet_name,)
        )
        result = self.cursor.fetchone()

        if result:
            return result[0]

        self.cursor.execute(
            "INSERT INTO diets (diet_name) VALUES (?)",
            (diet_name,)
        )
        self.connection.commit()

        return self.cursor.lastrowid
    # Breed query that will check for breed information and if non matching insert new breed into data
    def use_breed(self, breed_name, diet_name):

        diet_id = self.use_diet(diet_name)
        self.cursor.execute(
            "SELECT id FROM breeds WHERE breed_name = ?",
            (breed_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]

        self.cursor.execute(
            "INSERT INTO breeds (breed_name, diet_id) VALUES (?, ?)",
            (breed_name, diet_id)
        )
        self.connection.commit()

        return self.cursor.lastrowid
    # Create function for insertion of new animal data
    def create(self, data):
        # Verifying the input of data
        if data is None:
            raise Exception(
            "Nothing to save, because data parameter is empty")
        # MongoDB insertion
        if self.db_type == "mongo":
            self.collection.insert_one(data)
            return True
        # SQL insertion
        elif self.db_type == "sql":
            #Find diet ID
            diet_id = self.use_diet(data["diet"])
            #Find breed ID
            breed_id = self.use_breed(
                data["breed"],
                data["diet"]
            )
            # Execution of SQL command for insert statement
            # Cursor is used for SQL commands to interact with database
            # Question marks (?) are used as placeholders to bind values to the query to avoid injection attacks
            self.cursor.execute(
                # Insert of animal information
                "INSERT INTO animals (name, breed_id, diet_id, age) VALUES (?, ?, ?, ?)",
                (data["name"], breed_id, diet_id, data["age"])
            )
            # Commit saves insert
            self.connection.commit()
            return True
        
# Create method to implement the R in CRUD.
    def read(self, searchData):
        # Verifying the input of data
        if searchData is None:
            raise Exception("Nothing to see, because data parameter is empty")
        # MongoDB read dictionary query
        if self.db_type == "mongo":
            return self.collection.find(searchData)
        # SQL read query
        elif self.db_type == "sql":
            
            # INNER JOIN command to combine tables together
            self.cursor.execute("""            
                SELECT animals.name, animals.age, breeds.breed_name, diets.diet_name
                FROM animals
                JOIN breeds ON animals.breed_id = breeds.id
                JOIN diets ON animals.diet_id = diets.id
                WHERE breeds.breed_name = ?
            """, (searchData["breed"],)
            )
            # Return all results
            return self.cursor.fetchall()
    # Query function to find a dogs diet based on the breed of the aninmal       
    def diet_by_breed(self, breed_name):
        if self.db_type == "sql":
            # JOIN command to link diet table to breed table
            self.cursor.execute("""
                SELECT diets.diet_name
                FROM breeds
                JOIN diets ON breeds.diet_id = diets.id
                WHERE breeds.breed_name = ?
            """, (breed_name,))

            return self.cursor.fetchone()
# Update method to implement the U in CRUD
    def update(self, searchData, updateData):
        # Input and update verifications of input
        if not searchData:
            raise Exception("No value found to update")
        if not updateData:
            raise Exception("No update information to use")
        # MongoDB update query
        if self.db_type == "mongo":
            return self.collection.update_many(searchData, {"$set": updateData})
        # SQL update query
        elif self.db_type == "sql":
            # SQL cursor command to find breed ID
            self.cursor.execute(
                "SELECT id FROM breeds WHERE breed_name = ?",
                (searchData["breed"],)
            )
            # Returns result
            result = self.cursor.fetchone()

            if not result:
                return False
            
            breed_id = result[0]
            # Update animals age based on breed
            self.cursor.execute(
                "UPDATE animals SET age = ? WHERE breed_id = ?",
                (updateData["age"], breed_id)
            )
            # Save update to data    
            self.connection.commit()
            return True
            
# Delete method to implement the D in crud
    def delete(self, deleteData):
        # Verification of input
        if deleteData is None:
            raise Exception("No data found")
        # MongoDB delete query
        if self.db_type == "mongo":
            return self.collection.delete_one(deleteData)
        # SQL delete query
        elif self.db_type == "sql":
            self.cursor.execute(
                # Finding animal data based on breed
                "SELECT id FROM breeds WHERE breed_name = ?",
                (deleteData["breed"],)
            )
            # Return result
            result = self.cursor.fetchone()

            if not result:
                return False

            breed_id = result[0]
            # Deletes animals based on breed
            self.cursor.execute(
                "DELETE FROM animals WHERE breed_id = ?",
                (breed_id,) 
            )
            # Saves deletion of animals from data
            self.connection.commit()
            return True
            
# Creation of test file to run during local execution
if __name__ == "__main__":
    # Creation of test object to show success of SQL enhancements
    shelter = AnimalShelter(db_type = "sql")

    # Deletes rows from the animals table to reset the database if there are multiple test runs
    shelter.cursor.execute("DELETE FROM animals")
    shelter.cursor.execute("DELETE FROM breeds")
    shelter.cursor.execute("DELETE FROM diets")
    # Resets the counter for multiple runs for cleaner viewing
    shelter.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'animals'")
    # Saves changes to ensure reset of data table is stored
    shelter.connection.commit()
    # Confirmation output
    print("Reset of Database complete")

    # Output to show beginning of create method of testing
    print("\n create test")
    # Calling of create method and inserts multiple objects into table
    shelter.create({"name": "Bingo", "breed": "Lab", "diet": "High protein, Moderate-Fat", "age": 4})
    shelter.create({"name": "Ellie", "breed": "Golden Retriever","diet": "High animal protein", "age": 2})
    shelter.create({"name": "George", "breed": "Lab", "diet": "High protein, Moderate-Fat", "age": 7})
    shelter.create({"name": "Jupiter", "breed": "Lab", "diet": "High protein, Moderate-Fat", "age": 5})
    shelter.create({"name": "Ralph", "breed": "Pug", "diet": "High quality-protein, omega fatty acids", "age": 2})
    shelter.create({"name": "Ellie", "breed": "Lab", "diet": "High protein, Moderate-Fat", "age": 1})
    shelter.create({"name": "Link", "breed": "Golden Retriever","diet": "High animal protein", "age": 6})
    # Confirmation output
    print("Insert success")

    # Output for read method testing
    print("\n read test")
    # Calling of read method and stores object in results
    results = shelter.read({"breed": "Lab"})
    # Output confirmation displaying object stored in results variable
    print("Read results: ", results)

    # Output for update method testing
    print("\n update test")
    # Calls update method by breed and updates age
    shelter.update({"breed": "Golden Retriever"}, {"age": 5})
    # Calls read method and stores object in updated variable
    updated = shelter.read({"breed": "Golden Retriever"})
    # Confirmation output displaying updated object
    print("Updated: ", updated)

    # Output for delete method testing
    print("\n delete test")
    # Calls delete method and selects object by breed
    shelter.delete({"breed": "Lab"})
    # Calls read method to attempt to retrieve deleted data
    after_delete = shelter.read({"breed": "Lab"})
    # Confirmation output to show nothing after deletion
    print("Deleted: ", after_delete)
    #Test to confirm querying of diet by breed method
    print("\n Diet by Breed Test")
    diet = shelter.diet_by_breed("Lab")
    print("Diet for a Lab:", diet)
        
            
