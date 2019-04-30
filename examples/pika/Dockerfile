FROM python:3.6

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION

SHELL ["/bin/bash", "-c"]
WORKDIR /app/

COPY ./mgap /app/mgap
COPY examples/pika/recv_messages.py /app
COPY requirements.txt /app

RUN pip install --trusted-host pypi.python.org awscli --upgrade
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN useradd --no-log-init -m mgap
USER mgap

RUN aws configure --profile mgap set aws_access_key_id $AWS_ACCESS_KEY_ID
RUN aws configure --profile mgap set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
RUN aws configure --profile mgap set region $AWS_REGION

CMD ./recv_messages.py