#!/bin/bash

rsync -avzh --exclude='logs/'  ../web/ pi@192.168.0.105:/home/pi/sexysexyDer/web/
#rsync -avz --exclude "logs/" --exclude "downloads/" ../worker pi@192.168.0.105:/home/pi/sexysexyDer/worker/
#scp docker-compose.yml pi@192.168.0.105:/home/pi/sexysexyDer/docker-compose.yml
