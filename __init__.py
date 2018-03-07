from flask import Flask
from flask import jsonify
import ast
import json
from firebase import firebase
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
firebase = firebase.FirebaseApplication('',None)

#displays all events
@app.route('/')
def index():
	result= firebase.get('/events',None)
	return json.dumps(result)

#displays select events
@app.route('/retrieveEvent/<id>')
def retrieveEvents(id):
	result= firebase.get('/events/' +id,None)
	return json.dumps(result)

#give events within a certain distance from a location
@app.route('/getEvents/<location>/<distance>')
def getEvents(location,distance):
	result= firebase.get('/',None)
	start = "{\"events\": "

	result = ast.literal_eval(json.dumps(result))
	events = {}
	for event in result['events']:
		key = event
		#get event with the key
		eventDoc = result['events'][key]

		eventLocation = str(eventDoc['eventLocation'])

		#get its distance from user
		distanceBetween = haversine(location,eventLocation)

		if distanceBetween<float(distance):
			events[key] = eventDoc

	return json.dumps(events)


#this is used to calculate distance between two points
@app.route('/distCalc/<location1>/<location2>')
def getDist(location1,location2):
	distanceBetween = haversine(location1,location2)
	return str(distanceBetween)


#page used for testing
@app.route('/hello/<name>')
def hello(name):
    return "<h1>This page is no longer available</h1>"

#calculates distance betwwen t
def haversine(userLocation,eventLocation):
	radius = 6372.8 #earths radius(km)
	parsePoint = ','

	#parse the users location
	parseLocation = userLocation.rfind(parsePoint)
	userLat=float(userLocation[:parseLocation])
	userLong=float(userLocation[parseLocation+1:])

	#parse the location of the event
	parseLocation = eventLocation.rfind(parsePoint)
	eventLat=float(eventLocation[:parseLocation])
	eventLong=float(eventLocation[parseLocation+1:])

	#haversine formulae
	a = sin(radians(eventLat-userLat)/2)**2 + cos(radians(userLat)) * cos(radians(eventLat)) * sin(radians(eventLong-userLong)/2)**2
	b = 2*atan2(sqrt(a),sqrt(1-a))
	return float(b*radius)

def getBucket(location):
	bucketLoc = location.replace(".","_")

	parsePoint = ','

	#parse the users location
	parseLocation = bucketLoc.find(parsePoint)
	userLat=bucketLoc[:parseLocation] + "00"
	userLong=bucketLoc[parseLocation+1:] + "00"

	latParse = userLat.find("_")
	longParse = userLong.find("_")
	userLat = userLat[:latParse+3]
	userLong = userLong[:longParse+3]

	bucketLoc = userLat + "," + userLong

	return bucketLoc

if __name__=="__main__":
	app.run()
