from flask import Flask, request, redirect
import twilio.twiml
import argparse
import urllib
import time
import httplib, json, urllib

app = Flask(__name__)
 
callers = {
    "XXXXXXX": "Evan DeSantola",
}
class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)
def down(fileName):
    webFile=urllib.urlopen(fileName)
    output=open("symptoms.wav", "wb")
    output.write(webFile.read())
    output.close()

def speechToText():
	clientId = "XXXXXXXXXXXXXXXXXXXXXXx"
	clientSecret = "XXXXXXXXXXXXXXX"
	ttsHost = "https://speech.platform.bing.com"

	params = urllib.urlencode({'grant_type': 'client_credentials', 'client_id': clientId, 'client_secret': clientSecret, 'scope': ttsHost})

	print ("The body data: %s" %(params))

	headers = {"Content-type": "application/x-www-form-urlencoded"}

	AccessTokenHost = "oxford-speech.cloudapp.net"
	path = "/token/issueToken"

	# Connect to server to get the Oxford Access Token
	conn = httplib.HTTPSConnection(AccessTokenHost)
	conn.request("POST", path, params, headers)
	response = conn.getresponse()
	print(response.status, response.reason)

	data = response.read()
	conn.close()
	accesstoken = data.decode("UTF-8")
	print ("Oxford Access Token: " + accesstoken)

	#decode the object from json
	ddata=json.loads(accesstoken)
	access_token = ddata['access_token']

	# Read the binary from wave file
	f = open("symptoms.wav")
	try:
	    body = f.read();
	finally:
	    f.close()

	headers = {"Content-type": "audio/wav; samplerate=8000",
	"Authorization": "Bearer " + access_token}

	#Connect to server to recognize the wave binary
	conn = httplib.HTTPSConnection("speech.platform.bing.com")
	conn.request("POST", "/recognize/query?scenarios=ulm&appid=D4D52672-91D7-4C74-8AD8-42B1D98141A5&locale=en-US&device.os=wp7&version=3.0&format=json&requestid=1d4b6030-9099-11e0-91e4-0800200c9a66&instanceid=1d4b6030-9099-11e0-91e4-0800200c9a66", body, headers)
	response = conn.getresponse()
	print(response.status, response.reason)
	data = response.read()
	conn.close()
        return data
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    from_number = request.values.get('From', None)
    if from_number in callers:
        caller = callers[from_number]
    else:
        caller = "not evan"
    if caller=="not evan":
         return None
    resp = twilio.twiml.Response()
    # Greet the caller by name
    resp.say("Hello.  Welcome to WhatsUpDoc.")
    # Play an mp3
    #resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")
 
    # Gather digits.
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("""For the Medical Module, press 1.  For the weather module, press 2.""")
 
    return str(resp)
 
@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    """Handle key press from a user."""
 
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        resp = twilio.twiml.Response()
#WhatsUpDoc aims to provide information about common medical concerns telephonically to.  Please do not rely on WhatsUpDoc for diagnoses or definitive medical care.  Please enter your symptoms at the tone.
        resp.say("Hello, welcome to the medical module of WhatsUpDoc. ")
        resp.record(maxLength="30", action="/handle-recording")
        return str(resp)
 
    elif digit_pressed == "2":
        resp = twilio.twiml.Response()
        resp.say("This module is currently unavailable")
        return str(resp)
 
    # If the caller pressed anything but 1, redirect them to the homepage.
    else:
        return redirect("/")
 
@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():
    print "handle_recording"
    recording_url = request.values.get("RecordingUrl", None)
    print recording_url
    down(recording_url)
    resp = twilio.twiml.Response()
    print speechToText()
    resp.say("Thank you for choosing WhatsUpDoc.  These were your symptoms.  Goodbye.")

    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
