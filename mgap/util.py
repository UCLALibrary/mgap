def get_config():
    return {
        'aws': {
            'profile_name': ''
        },
        'clarifai': {
            'api_key': ''
        },
        'iiif': {
            'image_api_default_params': {
                'region': 'full',
                'size': 'full',
                'rotation': '0',
                'quality': 'default',
                'format': 'jpg'
            }
        },
        'rabbitmq': {
            'username': 'guest',
            'password': '',
            'host': 'localhost',
            'port': 5672,
            'vhost': ''
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': {
                'computer_vision_results': '0',
                'celery_task_results': '1'
            }
        },
        'web_annotation': {
            'annotation_seed': {
                '@context': 'http://www.w3.org/ns/anno.jsonld',
                'type': 'Annotation',
                'motivation': 'tagging',
                'target': {
                    'type': 'SpecificResource',
                    'selector': {
                        'type': 'ImageApiSelector'
                    }
                },
                'creator': {
                    'type': 'Organization',
                    'name': 'UCLA Library',
                    'homepage': 'https://library.ucla.edu'
                },
                'generator': {
                    'type': 'Software',
                    'name': 'Machine Generated Annotations Pipeline',
                    'homepage': 'https://github.com/UCLALibrary/mgap'
                }
            },
            'annotation_body_seed': {
                'type': 'TextualBody',
                'format': 'text/json',
                'language': 'en',
                'purpose': 'tagging',
                'creator': {
                    'type': 'Software'
                },
                'generator': {
                    'type': 'Software'
                }
            }
        }
    }
