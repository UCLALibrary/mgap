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
        }
    }
