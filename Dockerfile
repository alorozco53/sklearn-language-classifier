FROM ubuntu:16.04

# general
RUN apt-get update && apt-get install -y build-essential cmake \
    wget git unzip \
    yasm pkg-config software-properties-common python3-software-properties

# get python 3.6.3
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && \
    apt-get install -y python3.6 python3.6-dev python3.6-venv

# pip3 stuff
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.6 get-pip.py && \
    python3.6 -m pip install pip --upgrade

RUN rm -f /usr/bin/python && ln -s /usr/bin/python3.6 /usr/bin/python
RUN rm -f /usr/bin/python3 && ln -s /usr/bin/python3.6 /usr/bin/python3
RUN rm -f /usr/local/bin/pip && ln -s /usr/local/bin/pip3.6 /usr/local/bin/pip
RUN rm -f /usr/local/bin/pip3 && ln -s /usr/local/bin/pip3.6 /usr/local/bin/pip3

WORKDIR /

RUN mkdir /home/workspace
WORKDIR /home/workspace
COPY . /home/workspace

# install python dependencies
RUN apt-get install -y gcc python3.6-dev
RUN pip3 install sklearn
RUN pip3 install pandas
RUN pip3 install Flask
RUN pip3 install gunicorn
RUN pip3 install requests
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install python-dotenv

# Run app
EXPOSE 4000
ENV PYTHONIOENCODING=utf8
ENV LANG='en_US.UTF-8'
CMD python3.6 app.py
