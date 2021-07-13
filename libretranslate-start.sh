#!/bin/sh

port=5990

echo "Starting docker container on port ${port}"
docker run -ti --rm -p ${port}:${port} libretranslate/libretranslate
