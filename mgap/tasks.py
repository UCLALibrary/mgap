import json
from urllib.parse import urlparse, unquote

from arrow import now
from boto3 import Session as BotoSession
from botocore.client import Config as BotoConfig
from clarifai.rest import ClarifaiApp
from iiif.request import IIIFRequest
from redis import Redis
from requests import get

from .celery import app


# NOTE: for documentation of the `message` and `config` arguments of each task,
# see the constructor of `mgap.mgap.MGAP`.

@app.task
def get_image_url(message, config):
    '''Returns an image URL that conforms to the IIIF Image API.'''

    # The last path component is a URL-encoded identifier.
    iiif_image_server_base_url, url_encoded_identifier = message['iiif_image_info_url'].rsplit('/', maxsplit=1)

    # The `baseurl` keyword argument must have a trailing slash.
    image_api_request = IIIFRequest(baseurl=iiif_image_server_base_url + '/')
    image_api_params = {
        **config['iiif']['image_api_default_params'],
        'size': '640,',
        'identifier': unquote(url_encoded_identifier)
    }
    return image_api_request.url(**image_api_params)

@app.task
def send_to_amazon_rekognition(image_url, config, message):
    '''Sends an image to Amazon Rekognition.

    Args:
        image_url: The URL of the image to send to Amazon Rekognition.

    Returns:
        A dictionary containing the response payload from the computer vision
        service, a vendor identifier, and a timestamp.
    '''

    amazon_rekognition_client = BotoSession(profile_name=config['aws']['profile_name']).client('rekognition')
    timestamp = now('US/Pacific').isoformat()
    amazon_rekognition_response = amazon_rekognition_client.detect_labels(Image={'Bytes': get(image_url).content})

    return {
        'results': amazon_rekognition_response,
        'vendor': 'amazon_rekognition',
        'timestamp': timestamp
    }

@app.task
def send_to_clarifai(image_url, config, message):
    '''Sends an image to Clarifai.

    Args:
        image_url: The URL of the image to send to Clarifai.

    Returns:
        A dictionary containing the response payload from the computer vision
        service, a vendor identifier, and a timestamp.
    '''

    clarifai_client = ClarifaiApp(api_key=config['clarifai']['api_key'])
    clarifai_model = clarifai_client.public_models.general_model
    timestamp = now('US/Pacific').isoformat()
    clarifai_response = clarifai_model.predict_by_url(url=image_url)

    return {
        'results': clarifai_response,
        'vendor': 'clarifai',
        'timestamp': timestamp
    }

@app.task
def save_to_redis(computer_vision_results, config, message):
    '''Saves computer vision results to Redis as JSON.

    Args:
        computer_vision_results: A dictionary containing the response payload
            from the computer vision service, a vendor identifier, and a
            timestamp.

    Returns:
        The key under which the results were stored in Redis.
    '''

    redis_instance = Redis(
        host=config['redis']['host'],
        port=config['redis']['port'],
        db=config['redis']['db']
    )
    redis_key = message['iiif_image_info_url'] + '-' + computer_vision_results['vendor']
    redis_value = json.dumps({**message, **computer_vision_results})

    redis_instance.set(redis_key, redis_value)
    return redis_key
