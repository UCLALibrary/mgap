from celery import chain, group

from .tasks import *


class MGAP:
    def __init__(self, config, message):
        '''Creates a partial that is invoked for each message.

        Args:
            config: The return value of `mgap.util.get_config`. It is
                explicitly passed to every task in the pipeline, so that they
                can easily reference it.
            message: The body of the message representing a processing job. It
                is explicitly passed to every task in the pipeline EXCEPT for
                the first one (to which it is passed implicitly by `send`).
        '''

        # Don't forget .s() !!!
        # FIXME
        self.pipeline = chain(
            get_image_url.s(config),
            group(
                chain(
                    send_to_amazon_rekognition.s(config, message),
                    save_to_redis.s(config, message)
                ),
                chain(
                    send_to_clarifai.s(config, message),
                    save_to_redis.s(config, message)
                ),
                chain(
                    send_to_google_vision.s(config, message),
                    save_to_redis.s(config, message)
                )

            ),
            collect_computer_vision_results.s(config, message),
            construct_annotation.s(config, message),
            save_to_elucidate.s(config, message)
        )

    def send(self, x):
        '''Sends the parameter x down the pipeline.'''
        return self.pipeline(x)
