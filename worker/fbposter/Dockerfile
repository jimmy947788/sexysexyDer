FROM python:3.8-slim-buster

WORKDIR /usr/app

COPY worker/fbposter/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sexpackges/ ./sexpackges/
COPY worker/fbposter/src/ ./

CMD [ "python", "app.py" ]