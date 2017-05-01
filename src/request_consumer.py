import pika
import json
from init import init
import time


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='wordpress_details')


def process_request(ch, method, properties, body):
    form_data = json.loads(body)
    print "Start processing"
    init(form_data)
    print "Finished processing"


channel.basic_consume(process_request,
                      queue='wordpress_details',
                      no_ack=True)

channel.start_consuming()
