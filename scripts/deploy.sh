#!/bin/bash

rsync -avzh \
    --exclude logs/ \
    --exclude downloads/ \
    --exclude apache2/ \
    --exclude document/ \
    --exclude test/ \
    --exclude README.md \
    --exclude .git* \
    ../ pi@192.168.0.105:/home/pi/sexysexyDer/
