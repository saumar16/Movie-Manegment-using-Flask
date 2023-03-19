from flask import Flask, Response, request, render_template, jsonify
import pymongo
import json
import re
from bson.objectid import ObjectId


app=Flask(__name__)


try:
    mongo = pymongo.MongoClient(
    host = 'localhost',
    port = 27017,
    serverSelectionTimeoutMS = 1000
    )
    db = mongo.Database #connect to database
    mongo.server_info() #trigger exception if cannot connect to mongodb database
except:
    print("Error occured while connecting to mongodb database!!")


#   Requirement-1 Insert the new movie and show
@app.route('/api', methods=['POST'])
# user defined function to insert a new record and display
def insert_record():
  try:
      # getting user iput in json format
      recorddata = request.get_json()
      dbResponse = db.netflix.insert_one(recorddata)
      getdbrecord = list(db.netflix.find({"title":recorddata['title']}))
      
      result = [{record: data[record] for record in data if record != '_id'} for data in getdbrecord]
      response = Response(json.dumps({ "Response":"Successfully inserted a new record in database!!", "Inserted Record":f"{result}"}),status=201,mimetype='application/json')
      return response
  except Exception as exp:
      response = Response("Error occured while inserting new record!!",status=500,mimetype='application/json')
      return response


#	Requirement-2 Update the record using title. (By update only title, description and imdb score)
@app.route('/api/<string:title>', methods=['PATCH'])
def update_record_by_title(title):
    try:
        recorddata = request.get_json()
        getdbrecord1 = list(db.netflix.find({"title":title}))
        if getdbrecord1:
            # for record in getdbrecord1:
            dbResponse = db.netflix.update_many({"title":title},{'$set':{"title":recorddata["title"],"description":recorddata["description"],"imdb_score":recorddata["imdb_score"]}})
            getdbrecord = list(db.netflix.find({"title":recorddata["title"]}))
            result = [{record: data[record] for record in data if record != '_id'} for data in getdbrecord]
            return jsonify({ "Response":"Successfully updated the record in database!!", "Updated Record":f"{result}"})
        else:
            response = Response("Record Not Found with given title!!",status=500,mimetype='application/json')
            return response
    except Exception as exp:
        response = Response("Error occured while updating the record!!",status=500,mimetype='application/json')
        return response


#   Requirement-3 Delete the record using title
@app.route('/api/<string:title>', methods=['DELETE'])
def delete_record_by_title(title):
    try:
        getdbrecord = list(db.netflix.find({"title":title}))
        if getdbrecord:
            result = [{record: data[record] for record in data if record != '_id'} for data in getdbrecord]
            dbResponse = db.netflix.delete_many({"title":title})  
            response = Response(json.dumps({ "Response":"Successfully deleted the record in database!!", "Deleted Record":f"{result}"}),status=200,mimetype='application/json')
            return response
        else:
            response = Response("Record Not Found with given title!!",status=500,mimetype='application/json')
            return response
    except Exception as exp:
        response = Response("Error occured while deleting the record!!",status=500,mimetype='application/json')
        return response


#   Requirement-4 Retrieve all the records of movies and shows in database
@app.route('/api', methods=['GET'])
def get_all_records():
    try:
        getdbrecords = list(db.netflix.find())
        for record in getdbrecords:
            record['_id'] = str(record['_id'])
        print(getdbrecords)
        return Response(json.dumps(getdbrecords),status = 200,mimetype =("application/json"))
    except Exception as exp:
        response = Response("Error occured while fetching and displaying the records!!",status=500,mimetype='application/json')
        return response


#	Requirement-5 Display the movie and show’s detail using title
@app.route('/api/<string:title>', methods=['GET'])
def search_record_by_title(title):
    try:
        getdbrecord = list(db.netflix.find({'title': re.compile('^' + re.escape(title) + '$', re.IGNORECASE)}))
        if getdbrecord:
            result = [{record: data[record] for record in data if record != '_id'} for data in getdbrecord]
            
            return jsonify(result)
        else:
            response = Response("Record Not Found with given title!!",status=500,mimetype='application/json')
            return response
    except Exception as exp:
        response = Response("Error occured while fetching and displaying the record with given title!!",status=500,mimetype='application/json')
        return response


if __name__ == '__main__':
    app.run(port=3456, debug=True)