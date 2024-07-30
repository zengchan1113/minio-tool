FROM ubuntu:18.04

ADD ./minio_script.py .

RUN apt-get update -y && \
    apt-get install -y vim curl python3.7 python3-pip python3-dev && \
    ln -s /usr/bin/python3.7 /usr/bin/python &&\
    curl -o get-pip-3.7.py https://bootstrap.pypa.io/pip/3.7/get-pip.py && \
    python get-pip-3.7.py

RUN pip install minio environs
