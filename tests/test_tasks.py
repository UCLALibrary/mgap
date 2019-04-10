'''Tests for each Celery task.'''

import pytest
from json import load, loads
import urllib

import mgap.tasks, mgap.util


# --- FIXTURES --- #

@pytest.fixture(scope='module')
def mgap_config():
    '''Returns the MGAP configuration dictionary.'''
    return mgap.util.get_config()

@pytest.fixture(scope='module')
def messages():
    '''Returns a dictionary that contains one valid and one invalid MGAP message.'''
    ret = {}
    for x in ['valid', 'invalid']:
        with open('tests/fixtures/message_{}.json'.format(x), 'r') as message_file:
            ret[x] = load(message_file)
    return ret

@pytest.fixture(scope='module')
def computer_vision_results():
    '''Returns a dictionary representing the return value of mgap.tasks.collect_computer_vision_results.'''
    ret = {}
    for x in ['amazon_rekognition', 'clarifai']:
        with open('tests/fixtures/{}_results.json'.format(x), 'r') as computer_vision_results_file:
            ret[x] = load(computer_vision_results_file)
    return ret

# --- TESTS --- #

def test_get_image_url(messages, mgap_config):
    assert (mgap.tasks.get_image_url(messages['valid'], mgap_config)
        == '{}/full/640,/0/default.jpg'.format(messages['valid']['iiif_image_info_url']))

    # FIXME: use a more specific exception
    with pytest.raises(Exception):
        mgap.tasks.get_image_url(messages['invalid'], mgap_config)

def test_construct_annotation(computer_vision_results, messages, mgap_config):
    anno = mgap.tasks.construct_annotation(computer_vision_results, mgap_config, messages['valid'])
    anno_body = anno['body']

    # Annotation body is a non-empty list.
    assert type(anno_body) is list and len(anno_body) > 0

    # Body values are serialized JSON arrays of strings.
    for body in anno_body:
        body_value = loads(body['value'])
        assert type(body_value) is list and len(body_value) > 0
        for element in body_value:
            assert type(element) is str