from celery import Celery

from .util import get_config

config = get_config()
rabbitmq_config = config['rabbitmq']
redis_config = config['redis']

# Celery must be connected to a result backend in order to handle chords (which require synchronization).
# http://docs.celeryproject.org/en/latest/userguide/canvas.html#chord-important-notes
backend_url = 'redis://{}:{}/{}'.format(
    redis_config['host'],
    redis_config['port'],
    redis_config['db']['celery_task_results']
)
broker_url = 'amqp://{}:{}@{}:{}/{}'.format(
    rabbitmq_config['username'],
    rabbitmq_config['password'],
    rabbitmq_config['host'],
    rabbitmq_config['port'],
    rabbitmq_config['vhost']
)
app = Celery('mgap', backend=backend_url, broker=broker_url, include=['mgap.tasks'])

if __name__ == '__main__':
    app.start()
