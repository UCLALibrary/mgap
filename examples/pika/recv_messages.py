#!/usr/bin/env python

import json

import pika

from mgap.mgap import MGAP
from mgap.util import get_config


rabbitmq_config = get_config()['rabbitmq']

credentials = pika.credentials.PlainCredentials(
    rabbitmq_config['username'],
    rabbitmq_config['password']
)
connection_params = pika.ConnectionParameters(
    host=rabbitmq_config['host'],
    port=rabbitmq_config['port'],
    credentials=credentials,
)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

channel.queue_declare(queue='iiif_image')

pipeline = MGAP()
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    pipeline.send(json.loads(body.decode()))

channel.basic_consume(callback, queue='iiif_image', no_ack=True)

try:
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    print(' [*] Exiting.')
