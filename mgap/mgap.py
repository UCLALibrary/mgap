from celery import chain, group

from .tasks import *

class MGAP:
    def __init__(self):
        '''Creates a partial that is invoked for each image.'''

        # FIXME
        self.pipeline = group(
            chain(
                noop.s() |
                noop.s()
            ),
            noop.s()
        )

    def send(self, x):
        '''Sends the parameter x down the pipeline.'''
        return self.pipeline(x)
