docker pull balenalib/raspberry-pi-python


docker run -it --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp balenalib/raspberry-pi-debian-python:latest python web.py