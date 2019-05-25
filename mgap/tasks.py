from collections import Counter
import copy
import hashlib
import json
from urllib.parse import quote, unquote, urlparse

from arrow import now
from base64 import b64encode
from boto3 import Session as BotoSession
from botocore.client import Config as BotoConfig
from clarifai.rest import ClarifaiApp
from iiif.request import IIIFRequest
from pysolr import Solr
from redis import Redis
from requests import get, head, post, put

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
def send_to_google_vision(image_url, config, message):
    '''Sends an image to Google Vision service.

    Args:
        image_url: The URL of the image to send to Google.

    Returns:
        A dictionary containing the response payload from the computer vision
        service, a vendor identifier, and a timestamp.
    '''
    ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
    api_key = config['google_vision']['api_key']
    img_request = []

    ctxt = b64encode(get(image_url).content).decode()
    img_request.append({
        'image': {'content': ctxt},
        'features': [{
                        'type': 'OBJECT_LOCALIZATION',
                        'maxResults': 50
                    }]
        })

    json_data = json.dumps({"requests": img_request }).encode()
    timestamp = now('US/Pacific').isoformat()
    google_response = post(ENDPOINT_URL,
                    data=json_data,
                    params={'key': api_key},
                    headers={'Content-Type': 'application/json'})

    google_json = google_response.json()['responses']

    return {
        'results': google_json,
        'vendor': 'google_vision',
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

    # TODO: don't instantiate a Redis client for every task
    redis_instance = Redis(
        host=config['redis']['host'],
        port=config['redis']['port'],
        db=config['redis']['db']['computer_vision_results']
    )
    redis_key = message['iiif_image_info_url'] + '-' + computer_vision_results['vendor']
    redis_value = json.dumps({**message, **computer_vision_results})

    redis_instance.set(redis_key, redis_value)
    return redis_key

@app.task
def collect_computer_vision_results(redis_keys, config, message):
    '''
    Reads computer vision results from Redis, deserializes them, and stores
    them in a dictionary.

    Args:
        redis_keys: A list of Redis keys under which computer vision service
            results for the current image are stored.

    Returns:
        A dictionary representation of the computer vision results.
    '''

    redis_instance = Redis(
        host=config['redis']['host'],
        port=config['redis']['port'],
        db=config['redis']['db']['computer_vision_results']
    )
    return {redis_key: json.loads(redis_instance.get(redis_key)) for redis_key in redis_keys}

@app.task
def construct_annotation(computer_vision_results, config, message):
    '''Constructs a dictionary representing a WebAnnotation.

    Args:
        computer_vision_results: A dictionary representation of the computer
        vision results.

    Returns:
        A dictionary representing an annotation.
    '''

    # Start with base templates for the annotation and annotation body.
    anno = config['web_annotation']['annotation_seed']
    anno_body_seed = config['web_annotation']['annotation_body_seed']

    # FIXME: set id properly
    anno['id'] = 'FIXME'
    anno['body'] = []

    # Each annotation has multiple bodies, one for each CV service result.
    for k, v in computer_vision_results.items():
        anno_body = copy.deepcopy(anno_body_seed)
        if v['vendor'] == 'amazon_rekognition':
            image_tags = list(map(
                lambda x: x['Name'],
                v['results']['Labels']
            ))
            cv_service_name = 'Amazon Rekognition'
            cv_service_homepage = 'https://aws.amazon.com/rekognition'

        elif v['vendor'] == 'clarifai':
            image_tags = list(map(
                lambda x: x['name'],
                v['results']['outputs'][0]['data']['concepts']
            ))
            cv_service_name = 'Clarifai Predict'
            cv_service_homepage = 'https://www.clarifai.com/predict'
        
        elif v['vendor'] == 'google_vision':
            image_tags = list(map(
                lambda x: x['name'],
                v['results'][0]['localizedObjectAnnotations']
            ))
            cv_service_name = 'Google Computer Vision'
            cv_service_homepage = 'https://cloud.google.com/vision/'

        anno_body['value'] = json.dumps(image_tags)

        # Creator and generator is the same agent.
        anno_body['creator']['name'] = anno_body['generator']['name'] = cv_service_name
        anno_body['creator']['homepage'] = anno_body['generator']['homepage'] = cv_service_homepage
        anno_body['created'] = anno_body['generated'] = v['timestamp']

        # TODO: conditionally add modified field if annotation for current image already exists
        anno['body'].append(anno_body)

    anno['target']['source'] = message['iiif_image_info_url']
    anno['target']['selector']['region'] = '640,'
    anno['created'] = anno['generated'] = now('US/Pacific').isoformat()
    return anno

@app.task
def save_to_elucidate(annotation, config, message):
    '''Sends a request to Elucidate to create or update an annotation and its container.

    Args:
        annotation: A dictionary representation of a WebAnnotation.

    Returns:
        The URL of the annotation on Elucidate.
    '''

    elucidate_headers_seed = config['elucidate']['request_headers_seed']
    elucidate_base_url = '{}:{}/annotation/{}/'.format(
        config['elucidate']['host'],
        config['elucidate']['port'],
        config['elucidate']['annotation_model']
    )
    annotation_container_slug = hashlib.md5(message['item_ark'].encode("utf-8")).hexdigest()
    annotation_container_url = '{}{}/'.format(
        elucidate_base_url,
        annotation_container_slug
    )
    annotation_container_response = get(annotation_container_url)

    # If container doesn't exist for the ARK, create it.
    if annotation_container_response.status_code != 200:
        annotation_container = {
            **config['web_annotation']['annotation_container_seed'],
            'label': message['item_ark']
        }
        create_annotation_container_response = post(
            elucidate_base_url,
            headers={
                **elucidate_headers_seed,
                'Slug': annotation_container_slug
            },
            data=json.dumps(annotation_container, indent=4, sort_keys=True)
        )

        # Annotation couldn't have existed without a container, so create it.
        create_annotation_response = post(
            annotation_container_url,
            headers=elucidate_headers_seed,
            data=json.dumps(annotation, indent=4, sort_keys=True)
        )
        annotation_url = create_annotation_response.json().get('id')
    else:
        # Annotation container and annotation already exist, so update.
        annotation_url = annotation_container_response.json()['first']['items'][0]['id']

        # Extract the inner contents of the weak ETag (W/"...").
        etag = head(annotation_url).headers['etag'][3:-1]

        # FIXME: don't overwrite the annotation! Much of it might not have changed, so retain timestamps, etc.
        update_annotation_response = put(
            annotation_url,
            headers={
                **elucidate_headers_seed,
                'Content-Type': 'application/ld+json;profile="http://www.w3.org/ns/anno.jsonld"',
                'If-Match': etag
            },
            data=json.dumps(annotation, indent=4, sort_keys=True)
        )
    return annotation_url

@app.task
def save_to_blacklight_solr(computer_vision_results, config, message):
    '''Creates or updates the tags field on a image's Solr doc in each index.

    Args:
        computer_vision_results: A dictionary representation of the computer
        vision results.

    Returns:
        None
    '''
    def add_tags_to_solr_doc(index_id, document_id, tags):
        '''Adds a list of tags to the Solr document.

        Args:
            index_id: The name of the Solr index.
            document_id: The value of the id field of the Solr document to
                update.
            tags: A list of strings.

        Returns:
            None
        '''
        solr_client = Solr(config['solr']['indexes'][index_id], always_commit=True)

        tags_field = config['solr']['tags_field']
        copy_fields = config['solr']['copy_fields']

        # Get the value of each field to copy to the new document.
        src_fields = map(lambda x: x['src'], copy_fields)
        src_field_values = solr_client.search('id:{}'.format(document_id), fl=list(src_fields)).docs[0]

        # Only set the fields that are already set on the document.
        existing_src_fields = src_field_values.keys()

        # Add copy fields to the new Solr doc.
        solr_doc = {
            'id': document_id,
            tags_field: tags,
            **{copy_field['dst']: src_field_values[copy_field['src']] for copy_field in copy_fields if copy_field['src'] in existing_src_fields}
        }
        solr_client.add(
            [solr_doc],
            commitWithin='1000',
            fieldUpdates={
                tags_field: 'set',
                **{copy_field['dst']: 'set' for copy_field in copy_fields if copy_field['src'] in existing_src_fields}
            },
            overwrite=True
        )

    # Get the Solr id by transforming the reversed item ARK.
    solr_identifier = '-'.join(list(map(lambda x: x[::-1], message['item_ark'].split('/')))[1:][::-1])

    # Build up a list of combined image
    all_image_tags = []

    for k, v in computer_vision_results.items():

        # TODO: abstract this repeated code between here and `construct_annotation`
        if v['vendor'] == 'amazon_rekognition':
            image_tags = list(map(
                lambda x: x['Name'],
                v['results']['Labels']
            ))

        elif v['vendor'] == 'clarifai':
            image_tags = list(map(
                lambda x: x['name'],
                v['results']['outputs'][0]['data']['concepts']
            ))

        elif v['vendor'] == 'google_vision':
            image_tags = list(map(
                lambda x: x['name'],
                v['results'][0]['localizedObjectAnnotations']
            ))

        # If we're pointing to a service-specific index, write to it.
        index_name = v['vendor']
        if index_name in config['solr']['indexes']:
            add_tags_to_solr_doc(index_name, solr_identifier, image_tags)

        all_image_tags += image_tags

    # Write a combined list of tags to the combined index (all computer vision services).
    index_name = 'combined'
    if index_name in config['solr']['indexes']:
        add_tags_to_solr_doc(index_name, solr_identifier, list(Counter(all_image_tags)))
