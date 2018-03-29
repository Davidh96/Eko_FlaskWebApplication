from flask import Flask, request
from flask import jsonify
import ast
import json
from firebase import firebase
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error, mean_absolute_err

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
@app.route('/getEvents',methods=['POST'])
def getEvents():
	#get details from posted JSON
	location = request.json['location']
	distance = request.json['distance']
	userID = request.json['userID']

	result= firebase.get('/',None)

	events = {}
	for event in result['events']:
		key = event
		#get event with the key
		eventDoc = result['events'][key]

		eventLocation = str(eventDoc['eventLocation'])
		if(eventLocation!=""):
			#get its distance from user
			distanceBetween = haversine(location,eventLocation)

			if distanceBetween<float(distance):
				events[key] = eventDoc

	recKey = getRecommendation(userID,events)

	if recKey != "None":
		#reorganize json so rec appears first
		del events[recKey]
		result= firebase.get('/events/' + recKey,None)
		eventList={}
		eventList[recKey]=result
		eventList = json.dumps(eventList)[:-1] + "," + json.dumps(events)[1:]
		return eventList
	else:
		eventList = json.dumps(events)
	return eventList
	#return recKey

@app.route('/getRec',methods=['POST'])
def getRec():
	#
	result= firebase.get('/users',None)
	#userId = request.data
	rec = getRecommendation(request.data)
	return str(rec)

#this is used to calculate distance between two points
@app.route('/distCalc/<location1>/<location2>')
def getDist(location1,location2):
	distanceBetween = haversine(location1,location2)
	return str(distanceBetween)


#page used for testing
@app.route('/hello/<name>')
def hello(name):
    return "<h1>This page is no longer available</h1>"

def getRecommendation(userID,events):

	result= firebase.get('/',None)

	arr = list()
	userIds = list()
	#get rated events
	if firebase.get('/users',None) !=None:
		for user in result['users']:
		    userIds.append(user)
		    for event in result['users'][user]:
		        rating =result['users'][user][event]['rating']
		        arr.append(list([user,event,rating]))

	#get events the user has already rated
	alreadyRated = list()
	user = firebase.get('/users/' + userID,None)
	if user != None:
		for event in result['users'][userID]:
			alreadyRated.append(str(event))

	#create dataframe
	usrevntDF = pd.DataFrame(arr, columns = ['UserID', 'EventID', 'Rating'], dtype = int)
	eventsList = usrevntDF['EventID'].as_matrix()
	ratingsDF = usrevntDF.pivot(index = 'UserID', columns ='EventID', values = 'Rating')

	eventID = list()
	#get all events
	for event in events:
	    eventID.append(event)
	eventSet = set(ratingsDF.columns)
	eventList =set(eventID) - eventSet

	#add remaining events
	ratingsDF=pd.concat([ratingsDF,pd.DataFrame(columns=list(eventList))])

	train = ratingsDF.copy()

	#train = train.fillna(train.mean())
	train = train.fillna(0)

	ratingsDF = train.copy()

	#NEW STUFF
	R = ratingsDF.as_matrix()

	#matrix factorization
	#need to change k

	kNum =min(R.shape)-1
	if kNum>=1:
		U, sigma, Vt = svds(R,k = kNum)

		sigma = np.diag(sigma)

		predMat = np.dot(np.dot(U, sigma), Vt) + ratingMean.reshape(-1, 1)
		predDF = pd.DataFrame(predMat, columns = ratingsDF.columns)
		predDF.set_index([userIds],inplace=True)
		#
		#get user recommendation
		#remove already rated events
		if set(alreadyRated).issubset(predDF.columns):
			predDF.drop(alreadyRated,axis=1,inplace=True)
		temp = predDF.loc[userID].sort_values(ascending=False).copy()
		temp.index.name = "EventID"
		temp = temp.reset_index()

		temp = temp.head(1)
		temp = temp.iloc[0]['EventID']

	else:
		temp="None"
	return temp

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
