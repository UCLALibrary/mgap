'''Tests for each Celery task.'''

import pytest
from json import load
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

# --- TESTS --- #

def test_get_image_url(messages, mgap_config):
    assert (mgap.tasks.get_image_url(messages['valid'], mgap_config)
        == '{}/full/640,/0/default.jpg'.format(messages['valid']['iiif_image_info_url']))

    # FIXME: use a more specific exception
    with pytest.raises(Exception):
        mgap.tasks.get_image_url(messages['invalid'], mgap_config)