from flask import Flask, request
from flask import jsonify
import ast
import json
from firebase import firebase
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
import requests as rq
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error, mean_absolute_err

app = Flask(__name__)
firebase = firebase.FirebaseApplication('https://ekoapp-ba9b5.firebaseio.com/',None)

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

#add member to event
@app.route('/addMeber',methods=['POST'])
def addMeber():
	result = firebase.put('/events/-L9vhWFDVdP6iw7Jke4u','members', 'fuck')
	return "ok"

#get user details
@app.route('/readUserDetails/<userID>',methods=['GET'])
def readUserDetails(userID):
	result = firebase.get('/users/'+ userID,None)
	return json.dumps(result)

#update user details
@app.route('/updateUserDetails',methods=['POST'])
def updateUserDetails():
	user = request.json['userID']
	name = request.json['userName']
	token = request.json['userToken']
	key = request.json['userKey']

	#JSON format to be saved to database
	myObj = {
	    "DisplayName":name,
	    "PublicKey":key,
		"Token":token
	}

	result = firebase.put('/users',user,myObj)
	return user

#delete an event
@app.route('/deleteEvent/<eventID>',methods=['DELETE'])
def deleteEvent(eventID):
	firebase.delete('/events', eventID)
	return "user"

#delete a member from an event
@app.route('/deleteMember/<eventID>/<userID>',methods=['DELETE'])
def deleteMember(eventID,userID):
	result = firebase.get('/events/'+ eventID +'/members',None)
	#firebase.delete('/events/'+eventID,userID)
	temp="no"
	i=0
	for member in result:
	    if member['id']==userID:
	    	result.pop(i)
	    	temp="heya"
	    i+=1
	result = firebase.put('/events/'+eventID,'members',result)
	return json.dumps(result)

#add a meber to an event
@app.route('/addMember',methods=['POST'])
def addMember():
	eventID = request.json['eventID']
	userID = request.json['userID']
	result = firebase.get('/events/'+ eventID +'/members',None)

	myObj = {
	    "id":userID
	}

	result.append(myObj)
	result = firebase.put('/events/'+eventID,'members',result)
	return json.dumps(result)

#add rating of event
@app.route('/addRating',methods=['POST'])
def addRating():
	eventID = request.json['eventID']
	userID = request.json['userID']
	rating = request.json['Rating']

	myObj = {
	    "rating":rating
	}

	result = firebase.put('/users/'+ userID +'/rated', eventID,myObj)
	return json.dumps(result)

#post token
@app.route('/postToken',methods=['POST'])
def postToken():
	token = request.json['userToken']
	user = request.json['userID']
	result = firebase.put('/users/' + user,'Token',token)
	return str(result)

#post public key
@app.route('/postPublicKey',methods=['POST'])
def postPublicKey():
	key = request.json['userPublicKey']
	user = request.json['userID']
	result = firebase.put('/users/' + user,'PublicKey',key)
	return str(result)

#give events within a certain distance from a location
@app.route('/saveEvent',methods=['POST'])
def saveEvent():
	#get details from posted JSON
	authorName = request.json['eventAuthor']
	authorID = request.json['eventAuthorID']
	eventCategory = request.json['eventCategory']
	eventDate = request.json['eventDate']
	eventDescription = request.json['eventDescription']
	eventLocation = request.json['eventLocation']
	eventName = request.json['eventName']
	eventTime = request.json['eventTime']

	#set JSON object
	myObj = {
	    "eventAuthor":authorName,
	    "eventAuthorID":authorID,
		"eventCategory":eventCategory,
		"eventDate": eventDate,
		"eventDescription": eventDescription,
		"eventLocation": eventLocation,
		"eventName": eventName,
		"eventTime":eventTime,
		"id":"fuck",
	    "members": [
	        { "id":authorID}
	    ]
	}


	result = firebase.post('/events', myObj)
	result = firebase.put('/events/' + result['name'],'id', result['name'])
	return json.dumps(result)



#give events within a certain distance from a location
@app.route('/getEvents/<location>/<distance>')
def getEvents(location,distance):
	result= firebase.get('/',None)
	start = "{\"events\": "

	#result = json.dumps(result)
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


#give events within a certain distance from a location
@app.route('/getEventRecommendation',methods=['POST'])
def getEventRecommendation():
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
	#get recommended event
	if recKey != "None":
		result= firebase.get('/events/' + recKey,None)
		eventList={}
		eventList[recKey]=result
		return json.dumps(eventList)
	else:
	 	return "None"

	return json.dumps(result)


@app.route('/sendMsg',methods=['POST'])
def sendMsg():
	#authorization header
	headers = {'Content-Type': 'application/json',
	'Authorization': 'key=AAAAWO9bQgM:APA91bFj2RlhOMQopRZC2Ca-cSJ3wwFwKZyPeRO_RhUtiJ6YxR2utqRJ-olYSEhuN_86kjy2c_oZeNaNfh5SU3YPhPaIIbL5rew9vb-GMPVLgqJx7qrDxC9rdS0uCze2iGnun-l1oSgD'}

	#get contents of JSON
	msgTo = request.json['to']
	msgFromToken = request.json['fromToken']
	msgFromPublicKey = request.json['fromKey']
	msgFromID = request.json['fromID']
	msgFromName = request.json['fromName']
	msgData = request.json['data']


	#format that FCM server accepts
	url = 'https://fcm.googleapis.com/fcm/send'
	payload={
	 'to' : msgTo,
	 'data' : {
	     'fromToken': msgFromToken,
		 'fromKey' : msgFromPublicKey,
		 'fromID' : msgFromID,
	     'fromName' : msgFromName,
		 'msg' : msgData
	 }
	}

	r = rq.post(url, data=json.dumps(payload), headers=headers)

	return str(r)


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
	#check for only users that have rated stuff
	if firebase.get('/' + 'users',None) !=None:
		for user in result['users']:
			if firebase.get('/users/' + user + '/rated',None)!=None:
			    userIds.append(user)
			    for event in result['users'][user]['rated']:
			        rating =result['users'][user]['rated'][event]['rating']
			        arr.append(list([user,event,rating]))

	#get events the user has already rated
	alreadyRated = list()
	#check to see if user has actually rated anything
	user = firebase.get('/users/rated' + userID,None)
	if user != None:
		for event in result['users'][userID]['rated']:
			alreadyRated.append(str(event))

	#create dataframes
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

	#matrix factorization
	kNum =min(R_demeaned.shape)-1
	if kNum>=1:
		#perform svd
		U, sigma, Vt = svds(R_demeaned,k = min(R_demeaned.shape)-1)

		#convert sigma to diagonal matrix
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

#calculates distance betwwen two positions
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


if __name__=="__main__":
	app.run()
