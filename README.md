# Machine Generated Annotations Pipeline

## Installation

1. Install Python 3, AWS CLI, and a virtual environment manager.
2. Download and extract this repository.
3. In the repository directory, create and activate a virtual environment.
4. Install dependencies:

    ```bash
    $ pip install -r requirements.txt
    ```

5. Configure an AWS CLI profile with access tokens for Amazon Rekognition.
6. Obtain an API key for Clarifai.
7. Replace the dummy configuration data in `mgap.util.get_config`.

## Testing

At the project root directory, run:

```bash
$ pytest
```

## Usage

1. Move the example client scripts to the repository directory, so they can find the `mgap` package as an absolute import:

    ```bash
    $ mv examples/pika/*.py .
    ```

2. With the repository directory as the current working directory, Open three terminals:

    a. In the first, start the Celery worker:

    ```bash
    $ celery -A mgap worker -l info
    ```

    b. In the second, run the example recv script:

    ```bash
    $ ./recv_messages.py
    ```

    c. In the third, pipe some JSON to the example send script:

    ```bash
    $ echo '{ "iiif_image_info_url": "https://stacks.stanford.edu/image/iiif/gp903kf9548%2FSC1041_SAIL_Office_1979", "iiif_manifest_url": "https://purl.stanford.edu/gp903kf9548/iiif/manifest", "item_ark": "" }' | ./send_messages.py
    ```

