from flask import Flask,url_for, json, jsonify
from flask import request, Response
from functools import wraps
import logging

app=Flask(__name__)

@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/articles')
def api_articles():
    return 'List of ' + url_for('api_articles')

@app.route('/articles/<articleid>')
def api_article(articleid):
    return 'You are reading ' + articleid

# @app.route('/hello')
# def api_hello():
#     if 'name' in request.args:
#         return 'Hello' + request.args['name']
#     else:
#         return 'Hello Preeti'

@app.route('/echo', methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE' ])
# use "curl -X PUT http://127.0.0.1:5000/echo" to test
def api_echo():
	if request.method == 'GET':
		return "ECHO: GET\n"

	elif request.method == 'POST':
		return "ECHO: POST\n"

	elif request.method == 'PATCH':
		return "ECHO: PATCH\n"

	elif request.method == 'PUT':
		return "ECHO: PUT\n"

	elif request.method == 'DELETE':
		return "ECHO: DELETE"

# curl -H "Content-type: application/json" \
# -X POST http://127.0.0.1:5000/messages -d '{"message":"Hello Data"}'
@app.route('/message', methods=['POST'])
def api_message():
	if request.headers['Content-type'] == 'text/plain':
		return "Text Message: " + request.data

	elif request.headers['Content-type'] == 'application/json':
		return "JSON Message: " + json.dumps(request.json)

	elif request.headers['Content-type'] == 'application/octet-stream':
		f = open('./binary', 'wb')
		f.write(request.data)
		f.close()
		return "Binary message written"

	else:
		return "415 : Media type not supported"

# Responses
@app.route('/hello', methods=['GET'])
def api_hello():
	data = {
		'hello' : 'world',
		'number' : 3
	}
	js = json.dumps(data)
	resp = Response(js, status=200, mimetype='application/json') #mimetype is Content-type without additional info. It's useful when we have custom content types
	resp.headers['Link'] = 'http://google.com'
	return resp

# Status code and errors
@app.errorhandler(404)
def not_found(error=None):
	message = {
		'status': 404,
		'message': 'Not Found: ' + request.url
	}
	resp = jsonify(message)
	resp.status_code = 404

	return resp

@app.route('/user/<userid>', methods = ['GET'])
def api_users(userid):
	users = {'1': 'Preeti', '2': 'Jane', '3': 'Bhandari'}

	if userid in users:
		return jsonify({userid:users[userid]})   #will return {"1":"Preeti"}
	else:
		return not_found()

# Authorization
def check_auth(username, password):
	return username == 'admin' and password == 'secret'

def authenticate():            #if authentication failed, use this function to return a body
	message = {'message' : "authenticate"}
	resp = jsonify(message)

	resp.status_code= 401 #unauthorized access
	resp.headers['WWW-Authenticate'] = 'BasicRealm="Example"'

	return resp

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth:
			return authenticate()
		elif not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)

	return decorated

@app.route('/secrets')       # curl -v -u "admin:secret" http://127.0.0.1:5000/secrets        
@requires_auth
def api_whisper():
	return "SHHH, this is top secret stuff\n"
    
if __name__=='__main__':
    app.run()

##### CURL 

# option	purpose
# -X	specify HTTP request method e.g. POST
# -H	specify request headers e.g. "Content-type: application/json"
# -d	specify request data e.g. '{"message":"Hello Data"}'
# --data-binary	specify binary request data e.g. @file.bin
# -i	shows the response headers
# -u	specify username and password e.g. "admin:secret"
# -v	enables verbose mode which outputs info such as request and response headers and errors

