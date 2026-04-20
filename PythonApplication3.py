
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#from pymongo import MongoClient
#from bson.objectid import ObjectId

#Creation of class to handle CRUD design and implementation
class AnimalShelter:
    """ CRUD operations for Animal collection in MongoDB """

    #Constructor initialize connection with either MongoDB or testing data
    def __init__(self, USER = None, PASS = None, connect = False):
        
        #Flag determination to connect to MongoDB or use testing data locally
        self.connect = connect

        if self.connect:
            HOST = 'nv-desktop-services.apporto.com'
            PORT = 31382
            DB = 'AAC'
            COL = 'animals'
        #
        # Initialize Connection
        #
            self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
            self.database = self.client[DB]
            self.collection = self.database[COL]
            print ("Connection Successful")
        #Allows using test data for testing of sorting and filtering algorithms later
        #This data will help to show that the implementation of the algorithms work without connecting to database
        else:
            self.test_data = [
                {"animal_type": "Dog", "breed": "Labrador", "age": 3},
                {"animal_type": "Dog", "breed": "Rottweiler", "age": 5},
                {"animal_type": "Dog", "breed": "Husky", "age": 2},
                {"animal_type": "Dog", "breed": "Beagle", "age": 3}
            ]
            #Output to let user know test mode has been accessed
            print("test mode")
    
    #Helper method object for sorting algorithm to normalize values for consistency
    def _get_sort_value(self, item, sortField):
        value = item.get(sortField, "")
        value = str(value)
        value = value.lower()
        return value

    #Creation of the insertion sorting algorithm
    def _insertion_sort(self, data, sortField):

        #Create a copy of the list so that original data does not get modified
        arr = data[:]

        #Begin looping through list starting at index 1
        for i in range(1, len(arr)):
            #Current item to be inserted into sorted portion of list
            current_item = arr[i]
            #Use of created object to ensure sorted value will be consistent for successful sorting
            current_value = self._get_sort_value(current_item, sortField)

            #Begin backwards comparison
            j = i - 1

            #Loop to shift larger items
            while j >= 0 and self._get_sort_value(arr[j], sortField) > current_value:
                #Shifting of items on position to the right
                arr[j + 1] = arr[j]
                j -= 1

            #Insertion of current item into correct sorted position
            arr[j + 1] = current_item
        
        #Returning of sorted list
        return arr

#Original create method to implement the C in CRUD.
    def create(self, data):
        if data is not None:
            self.database.animals.insert_one(data)
            return True
        else:
            raise Exception(
            "Nothing to save, because data parameter is empty")


    #Modified read to implement algorithmic sorting enhancement
    #Adding sortField will give the option for sorting data
    #Adding reverse will give option for sorting to be in alphabetical order or reverse alphabetical order
    #Created branches for testing functionality of algorithm with a set of local data
    #Also created capabilities for choosing between sorting with two different algorithms for comparison purposes

    #Enhanced read capabilities for CRUD design
    def read(self, searchData, sortField = None, reverse = False, sortMethod = "timsort"):

        #Ensure searchData (dictionary) is given
        if searchData is None:
            raise Exception("Nothing to see, because data parameter is empty")
            
        #Testing branch when no connection to database
        if not self.connect:
            #create empty list
            results = []
            #loop for animals in test data set
            for item in self.test_data:
                match = True
                #loop for search conditions
                for k, v in searchData.items():
                    #Get a value and ensure that it will match data without case or white space sensitivity
                    if str(item.get(k,"")).strip().lower() != str(v).strip().lower():
                        match = False
                        break
                #adds items to results if match success
                if match:
                    results.append(item)

        #connection to database when not running test mode
        else:
            #converts data into a list
            results = list(self.collection.find(searchData))
        
        #This print line was added for debugging purposes while attempting test runs and ran into issues
        #print("Before", results)
        
        #Checks for sorting information from user and allows different sort algorithms
        if sortField:
            print("sort by:", sortField)
            print("method:", sortMethod)

            #Running insertion sort algorithm with data
            if sortMethod == "insertion":
                results = self._insertion_sort(results, sortField)

                if reverse:
                    results.reverse()

            #Use of sorting algorithm built-in Python Timsort algorithm which users 
            #can apply based on different attributes with the data
            else:
                results = sorted(
                    #lambda is used for definition of normalized sort value for each item
                    results, key=lambda x: self._get_sort_value(x, sortField), reverse=reverse
                )

        #This print line added for debugging purposes when trying to get test run functioning
        #print("After", results)
        
        return results
        
#Original update method to implement the U in CRUD
    def update(self, searchData, updateData):
        if not searchData:
            raise Exception("No value found to update")
        elif not updateData:
            raise Exception("No update information to use")
        else:    
            if updateData is not None:
                data = self.database.animals.update_many(searchData, {"$set": updateData})
                return data

#Original delete method to implement the D in crud
    def delete(self, deleteData):
        if deleteData is not None:
            data = self.database.animals.delete_one(deleteData)
            return data
        else: 
            raise Exception("No data found")

#Main execution if connection is not made to show confirmation of test runs with sorting options
if __name__ == "__main__":

    #Creation of object in test mode
    shelter = AnimalShelter(connect = False)

    #Output showing user they are running the Timsort algorithm
    print("\nTimsort algorithm")
    results = shelter.read(
        {"animal_type": "Dog"},
        sortField = "breed",
        sortMethod = "timsort"
    )

    #Output of sorted data after Timsort algorithm completion
    print("Sorted Dogs:")
    for animal in results:
        print(animal)
    
    #Output showing user they are running the Insertion sort algorithm
    print("\n Insertion Sort algorithm")
    results = shelter.read(
        {"animal_type": "Dog"},
        sortField = "age",
        sortMethod = "insertion"
    )

    #Output of sorted data after Insertion algoritm completion
    print("Sorted Dogs:")
    for animal in results:
        print(animal)