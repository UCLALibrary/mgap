# Machine Generated Annotations Pipeline
[![Build Status](https://travis-ci.org/UCLALibrary/mgap.svg?branch=master)](https://travis-ci.org/UCLALibrary/mgap)


## Installation

1. Install Docker and Docker Compose.
2. Download and extract this repository.
3. Obtain access to Amazon Rekognition and Clarifai.
4. Stand up and configure instances of the following:

    - [Blacklight](http://projectblacklight.org) (at least one instance)
    - [IIIF](https://iiif.io) image server
    - [Elucidate](https://github.com/dlcs/elucidate-server) WebAnnotation server
    - RabbitMQ

5. Fill in the blanks in `.env`.
6. Fill in the blanks and replace the dummy configuration data in `mgap.util.get_config`.
7. Bring up the containers on your Docker host:

    ```bash
    docker-compose up -d
    ```

## Testing

At the project root directory, run:

```bash
$ pytest
```

## Usage

### Terminal 1

1. Bring up the containers on your Docker host, if you haven't already:

    ```bash
    docker-compose up -d
    ```

### Terminal 2

1. Install Python 3.5, or 3.6, and a Python virtual environment manager.
2. In the repository directory, create and activate a virtual environment:

    ```bash
    # GNU/Linux
    python -m venv venv_mgap
    . venv_mgap/bin/activate
    ```

3. Install dependencies:

    ```bash
    $ pip install -r requirements.txt
    ```

4. Move the example send script to the repository directory, so it can find the `mgap` package as an absolute import:

    ```bash
    $ mv examples/pika/send_messages.py .
    ```

5. Pipe some JSON to the example send script:

    ```bash
    $ echo '{ "iiif_image_info_url": "https://stacks.stanford.edu/image/iiif/gp903kf9548%2FSC1041_SAIL_Office_1979", "iiif_manifest_url": "https://purl.stanford.edu/gp903kf9548/iiif/manifest", "item_ark": "ark:/00000/aaa.bbb" }' | ./send_messages.py
    ```
