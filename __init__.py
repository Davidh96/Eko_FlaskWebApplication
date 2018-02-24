from flask import Flask
from flask import jsonify
import json
from firebase import firebase
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
firebase = firebase.FirebaseApplication('',None)

#displays all events
@app.route('/')
def index():
	result= firebase.get('/',None)
	result=str(cleanJson(str(result)))
	return str(result)

#displays all events
@app.route('/getEvents/<location>/<distance>')
def locationRoute(location,distance):
	bucketLoc = getBucket(location)

	result= firebase.get('/events/' + bucketLoc,None)
	result="{ u'events': " +str(result)+ "}"

	result = cleanJson(result)
	data = json.loads(result)

	events="{u'events': "

	for event in data["events"]:
		keyStartPos = str(event).find("-")
		keyEndPos = str(event).find("\':")

	 	key = str(event)[keyStartPos:keyEndPos]

		eventLocation = str(event[key]['eventLocation'])
		#get its distance from user

	 	distanceBetween = haversine(location,eventLocation)

	 	if distanceBetween<float(distance):
			events = events + str(event) + ","

	#end events string
	events = events[:len(events)-1] + "}"

	return cleanJson(str(events))
	#return userLat + "," + userLong

#tidies up JSON before displaying
def cleanJson(result):
		eventsString = "u'events': "
		json = str(result)
		newEventString ="}, u'"

		#find start of events list
		position =json.find(eventsString) + len(eventsString)

		#place events into array
		json = json[:position] + "[" + json[position:]

		position = json.rfind('}')

		json = json[:position] + "]" + json[position:]

		json = json.replace(newEventString,"}},{u'")

		#remove unicode charachter
		json=removeUnicode(json)

		return(json)

#removes the unicode charachter
def removeUnicode(json):
			unicodeChar1 = "u'"
			unicodeChar2 = 'u"'

			json = json.replace(unicodeChar1,"\"")
			json = json.replace(unicodeChar2,"\"")
			#json 'loads' accepts strings with double quotes
			json= json.replace("':","\":")
			json= json.replace("',","\",")
			json= json.replace("'}","\"}")
			return json

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
# #displays select events
# @app.route('/retrieveEvents/<id>')
# def retrieveEvents(id):
# 	result= firebase.get('/events/'+id,None)
# 	return removeUnicode(str(result))

#displays select events
@app.route('/retrieveEvent/<location>/<id>')
def retrieveEvent(location,id):

	bucketLoc = getBucket(location)
	result= firebase.get('/events/' + bucketLoc + '/' + id,None)
	#result= firebase.get('/events/'+id,None)
	return removeUnicode(str(result))

# #give events within a certain distance from a location
# @app.route('/getEvents/<location>/<distance>')
# def getEvents(location,distance):
# 	result= firebase.get('/',None)
# 	temp=str(cleanJson(str(result)))
#
# 	#places data into json object
# 	data  = json.loads(temp)
# 	events="{u'events': "
#
# 	for event in data["events"]:
# 		keyStartPos = str(event).find("-")
# 		keyEndPos = str(event).find("\':")
#
# 		key = str(event)[keyStartPos:keyEndPos]
#
# 		eventLocation = str(event[key]['eventLocation'])
# 		#get its distance from user
#
# 		distanceBetween = haversine(location,eventLocation)
#
# 		if distanceBetween<float(distance):
# 			events = events + str(event) + ","
#
# 	#end events string
# 	events = events[:len(events)-1] + "}"
#
# 	return cleanJson(str(events))

#this is used to calculate distance between two points
@app.route('/distCalc/<location1>/<location2>')
def getDist(location1,location2):
	distanceBetween = haversine(location1,location2)
	return str(distanceBetween)


#page used for testing
@app.route('/hello/<name>')
def hello(name):
    return "<h1>This page is no longer available</h1>"

if __name__=="__main__":
	app.run()
