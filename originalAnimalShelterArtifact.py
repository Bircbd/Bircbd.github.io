# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, USER, PASS):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the 
        # animals collection, and the aac user.
        # Definitions of the connection string variables are
        # unique to the individual Apporto environment.
        #
        # You must edit the connection variables below to reflect
        # your own instance of MongoDB!
        #
        # Connection Variables
        #
        #USER = 'aacuser'
        #PASS = '1234SnHu'
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

# Complete this create method to implement the C in CRUD.
    def create(self, data):
        if data is not None:
            self.database.animals.insert_one(data)
            return True
        else:
            raise Exception(
            "Nothing to save, because data parameter is empty")

# Create method to implement the R in CRUD.
    def read(self, searchData):
        if searchData is not None:
            data =self.database.animals.find(searchData)
            return data
        else:
            raise Exception("Nothing to see, because data parameter is empty")

# Create an update method to implement the U in CRUD
    def update(self, searchData, updateData):
        if not searchData:
            raise Exception("No value found to update")
        elif not updateData:
            raise Exception("No update information to use")
        else:    
            if updateData is not None:
                data = self.database.animals.update_many(searchData, {"$set": updateData})
                return data

#Create a delete method to implement the D in crud
    def delete(self, deleteData):
        if deleteData is not None:
            data = self.database.animals.delete_one(deleteData)
            return data
        else: 
            raise Exception("No data found")
            