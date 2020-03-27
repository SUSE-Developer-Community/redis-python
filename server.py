from flask import Flask, redirect, render_template, request
import json
import os
import redis

APP_PORT = 8080
APP_HOST = "0.0.0.0"

app = Flask(__name__)

cf_app_env = os.getenv('VCAP_APPLICATION')
if cf_app_env is not None:
    host = json.loads(cf_app_env)['application_uris'][0]
else:
    host = 'localhost'

if 'VCAP_SERVICES' in os.environ:
	vcap_services = json.loads(os.environ['VCAP_SERVICES'])
	if 'redis' in vcap_services:
		credentials = vcap_services['redis'][0]['credentials']
		redis_host = credentials['host']
		redis_port = credentials['port']
		redis_password = credentials['password']
	else:
		print("No Redis info found in VCAP_SERVICES! Are you sure you created and bound the service to your app?")

try:
	r = redis.Redis(
		host = redis_host,
		port = redis_port,
		password = redis_password
		)
except redis.ConnectionError:
	print("Error connecting to Redis database!")
	r = None

@app.route('/')
def index():
	redis_words = r.lrange("mywords", 0, -1)
	return render_template('index.html', redis_words=list(redis_words))

@app.route('/addvalue', methods=['POST'])
def add_value():
	value = request.form['value']
	print("Received value " + value + ", adding to database...")
	r.rpush("mywords", value)
	return redirect("/", code=302)

@app.route('/removevalue', methods=['POST'])
def remove_value():
	value = request.form['value']
	print("Received value " + value + ", removing from database...")
	r.lrem("mywords", 0, value)
	return redirect("/", code=302)

if __name__ == '__main__':
	app.run(host=APP_HOST, port=APP_PORT)
