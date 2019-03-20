#!/usr/bin/env python

import json

from kombu import Connection, Exchange, Queue

from mgap.mgap import MGAP
from mgap.util import get_config


config = get_config()
rabbitmq_config = config['rabbitmq']

broker_url = 'amqp://{}:{}@{}:{}/{}'.format(
    rabbitmq_config['username'],
    rabbitmq_config['password'],
    rabbitmq_config['host'],
    rabbitmq_config['port'],
    rabbitmq_config['vhost']
)

media_exchange = Exchange('', 'direct', durable=False)
iiif_image_queue = Queue('iiif_image', exchange=media_exchange, durable=False, routing_key='iiif_image')

def process_iiif_image(body, message):
    print(" [x] Received %r" % body)
    parsed_message = json.loads(body)

    pipeline = MGAP(config, parsed_message)
    pipeline.send(parsed_message)
    message.ack()

try:
    with Connection(broker_url) as conn:

        with conn.Consumer([iiif_image_queue], callbacks=[process_iiif_image]) as consumer:
            print(' [*] Waiting for messages. To exit press CTRL+C')
            while True:
                conn.drain_events()
except KeyboardInterrupt:
    print(' [*] Exiting.')
