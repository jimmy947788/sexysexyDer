FROM python:3.8-slim-buster

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./

CMD [ "python", "app.py" ]