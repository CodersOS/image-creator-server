FROM ubuntu

RUN apt-get update && \
    apt-get -y install python3 python3-pip && \
    wget -O- https://get.docker.com | bash && \
    apt-get clean

ADD requirements.txt /root/requirements.txt

RUN pip3 install -r /root/requirements.txt && rm -f /root/requirements.txt

ADD LICENSE /root/codersos_image_server/LICENSE
ADD codersos_image_server /root/codersos_image_server

WORKDIR /root
COMMAND ["python3", "-m", "codersos_image_server.app"]