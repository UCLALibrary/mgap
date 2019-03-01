#!/usr/bin/env python

import fileinput
import json

from kombu import Connection, Exchange, Queue

from mgap.util import get_config


rabbitmq_config = get_config()['rabbitmq']

broker_url = 'amqp://{}:{}@{}:{}/{}'.format(
    rabbitmq_config['username'],
    rabbitmq_config['password'],
    rabbitmq_config['host'],
    rabbitmq_config['port'],
    rabbitmq_config['vhost']
)

media_exchange = Exchange('', 'direct', durable=False)
iiif_image_queue = Queue('iiif_image', exchange=media_exchange, durable=False, routing_key='iiif_image')

with Connection(broker_url) as conn:
    with conn.Producer(serializer='json') as producer:
        for line in fileinput.input():
            producer.publish(
                line,
                exchange=media_exchange,
                routing_key='iiif_image',
                declare=[iiif_image_queue]
            )
            print(" [x] Sent '{}'".format(line))
