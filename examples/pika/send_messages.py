#!/usr/bin/env python

import fileinput

import pika

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

for line in fileinput.input():
    channel.basic_publish(exchange='', routing_key='iiif_image', body=line)
    print(" [x] Sent '{}'".format(line))
connection.close()
