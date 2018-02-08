from flask import Flask
from flask import jsonify
from firebase import firebase
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
firebase = firebase.FirebaseApplication('https://ekoapp-ba9b5.firebaseio.com/',None)

#displays all events
@app.route('/')
def index():
	result= firebase.get('/',None)
	return str(cleanJson(result))

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

		return(json)

#removes the unicode charachter
def removeUnicode(formatedJSON):
			unicodeChar = "u'"

			formatedJSON = formatedJSON.replace(unicodeChar,"'")
			return formatedJSON

def haversine(userLat,userLong,eventLat,eventLong):
	radius = 6372.8 #earths radius(km)
	#haversine formulae
	a = sin(radians(eventLat-userLat)/2)**2 + cos(radians(userLat)) * cos(radians(eventLat)) * sin(radians(eventLong-userLong)/2)**2
	b = 2*atan2(sqrt(a),sqrt(1-a))
	return b*radius

#displays select events
@app.route('/retrieveEvents/<id>')
def retrieveEvents(id):
	result= firebase.get('/events/'+id,None)
	return removeUnicode(str(result))

@app.route('/getEvents/<location>')
def getEvents(location):
	parsePoint = ','
	parseLocation = location.rfind(parsePoint)
	latitude=location[:parseLocation]
	longitude=location[parseLocation+1:]

	return str(haversine(35,-6,35.1,-6.1))

#page used for testing
@app.route('/hello/<name>')
def hello(name):
    return "<h1>This page is no longer available</h1>"



if __name__=="__main__":
	app.run()
