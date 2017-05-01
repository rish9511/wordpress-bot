import pika
import json
from init import init

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='wordpress_details')


def process_request(ch, method, properties, body):
    form_data = json.loads(body)
    init(form_data)
    print "finished processing"

channel.basic_consume(process_request,
                      queue='wordpress_details',
                      no_ack=True)

channel.start_consuming()
