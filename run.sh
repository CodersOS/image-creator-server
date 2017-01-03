#!/bin/bash

docker build -t codersos/image-creator-server . && docker run --rm codersos/image-creator-server