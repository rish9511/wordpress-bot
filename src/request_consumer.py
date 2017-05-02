import pika
import json
from init import init
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat_interval=0))
channel = connection.channel()

channel.queue_declare(queue='wordpress_details', durable=True)


def process_request(ch, method, properties, body):
    form_data = json.loads(body)
    print "Start processing"
    start = time.time()
    init(form_data)
    end = time.time()
    print "\nFinished processing"
    print "\ntook %f seconds to process" % (end - start)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(process_request,
                      queue='wordpress_details')

channel.start_consuming()
