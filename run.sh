#!/bin/bash

docker build -t codersos/image-creator-server . && docker run --rm -v /var/run/docker.sock:/var/run/docker.sock codersos/image-creator-server