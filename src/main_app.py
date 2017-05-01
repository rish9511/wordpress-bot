from flask import Flask
from flask import render_template
from flask import request
import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='wordpress_details')


app = Flask(__name__)


@app.route('/details', methods=['POST', 'GET'])
def process_details():

	if request.method == "POST":
		form_data = json.dumps(request.json)
		if form_data:
				channel.basic_publish(exchange='', routing_key='wordpress_details', body=form_data)
				connection.close()

	return ""


@app.route('/')
def index():
		return render_template("homepage.html")


if __name__ == "__main__":
	app.run()
