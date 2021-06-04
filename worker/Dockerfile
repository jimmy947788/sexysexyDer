FROM balenalib/raspberry-pi-debian-python:latest

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./

CMD [ "python", "app.py" ]