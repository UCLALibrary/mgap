from celery import Celery

from .util import get_config

rabbitmq_config = get_config()['rabbitmq']

broker_url = 'amqp://{}:{}@{}:{}/{}'.format(
    rabbitmq_config['username'],
    rabbitmq_config['password'],
    rabbitmq_config['host'],
    rabbitmq_config['port'],
    rabbitmq_config['vhost']
)
app = Celery('mgap', broker=broker_url, include=['mgap.tasks'])

if __name__ == '__main__':
    app.start()
