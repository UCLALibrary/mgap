def get_config():
    return {
        'aws': {
            'profile_name': 'mgap'
        },
        'clarifai': {
            'api_key': ''
        },
        'elucidate': {
            'host': 'http://localhost',
            'port': 8080,
            'base_path': '/annotation',
            'annotation_model': 'w3c',
            'request_headers_seed': {
                'Accept': 'application/ld+json;profile="http://www.w3.org/ns/anno.jsonld"',
                'Content-Type': 'application/ld+json'
            }
        },
        'google_vision': {
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
            'host': 'redis',
            'port': 6379,
            'db': {
                'computer_vision_results': '0',
                'celery_task_results': '1'
            }
        },
        'solr': {
            'indexes': {
                'amazon_rekognition': 'http://localhost:8983/solr/amazon_rekognition',
                'clarifai': 'http://localhost:8983/solr/clarifai',
                'google_vision': 'http://localhost:8983/solr/google_vision',
                'combined': 'http://localhost:8983/solr/combined'
            },
            'tags_field': 'tags_ssim',
            'copy_fields': [
                {
                    'src': 'subject_tesim',
                    'dst': 'subject_sim'
                },
                {
                    'src': 'human_readable_type_tesim',
                    'dst': 'human_readable_type_sim'
                },
                {
                    'src': 'human_readable_resource_type_tesim',
                    'dst': 'human_readable_resource_type_sim'
                },
                {
                    'src': 'genre_tesim',
                    'dst': 'genre_sim'
                },
                {
                    'src': 'named_subject_tesim',
                    'dst': 'named_subject_sim'
                },
                {
                    'src': 'location_tesim',
                    'dst': 'location_sim'
                },
                {
                    'src': 'language_tesim',
                    'dst': 'language_sim'
                }
            ]
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
            },
            'annotation_container_seed': {
                '@context': 'http://www.w3.org/ns/anno.jsonld',
                'type': 'AnnotationCollection'
            }
        }
    }
