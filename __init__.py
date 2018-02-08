from flask import Flask
from flask import jsonify
from firebase import firebase


app = Flask(__name__)
firebase = firebase.FirebaseApplication('',None)

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

#displays select events
@app.route('/retrieveEvents/<id>')
def retrieveEvents(id):
	result= firebase.get('/events/'+id,None)
	return removeUnicode(str(result))

#page used for testing
@app.route('/hello/<name>')
def hello(name):
    return "<h1>This page is no longer available</h1>"



if __name__=="__main__":
	app.run()
