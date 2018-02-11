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

#tidies up JSON before displaying
def cleanJson(result):
		eventsString = "{'events': "
		json = str(result)
		newEventString ="}, '"

		#remove unicode charachter
		json=removeUnicode(json)

		#find start of events list
		position =json.find(eventsString) + len(eventsString)

		#place events into array
		json = json[:position] + "[" + json[position:]

		position = json.rfind('}')

		json = json[:position] + "]" + json[position:]

		json = json.replace(newEventString,"}},{'")

		#json 'loads' accepts strings with double quotes
		json= json.replace("':","\":")
		json= json.replace("',","\",")
		json= json.replace("'}","\"}")

		return(json)

#removes the unicode charachter
def removeUnicode(formatedJSON):
			unicodeChar = "u'"

			formatedJSON = formatedJSON.replace(unicodeChar,"\"")
			return formatedJSON

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
	return b*radius

#displays select events
@app.route('/retrieveEvents/<id>')
def retrieveEvents(id):
	result= firebase.get('/events/'+id,None)
	return removeUnicode(str(result))

#give events within a certain distance from a location
@app.route('/getEvents/<location>/<distance>')
def getEvents(location,distance):
	result= firebase.get('/',None)
	temp=str(cleanJson(str(result)))

	#places data into json object
	data  = json.loads(temp)
	events='{"events":'

	#go through events
	for event in data['events']:
		temp=removeUnicode(str(event))
		#event key
		temp = temp[2:22]
		#get event location
		eventlocation = event[temp]['eventLocation']
		#get its distance from user
		distanceBetween = haversine(location,eventlocation)
		#if event is within defined distance, add it to be returned to user
		if float(distanceBetween)<=float(distance):
			events = events + str(event) + ","

	#end events string
	events = events[:len(events)-1] + "}"
	#return list
	return cleanJson(str(events))


#page used for testing
@app.route('/hello/<name>')
def hello(name):
    return "<h1>This page is no longer available</h1>"

if __name__=="__main__":
	app.run()
