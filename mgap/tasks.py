from urllib.parse import urlparse, unquote

from arrow import now
from boto3 import Session as BotoSession
from botocore.client import Config as BotoConfig
from iiif.request import IIIFRequest
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
