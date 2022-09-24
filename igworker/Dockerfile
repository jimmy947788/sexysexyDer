FROM python:3.8-slim-buster

WORKDIR /app

COPY ./igworker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sexpackges/ ./sexpackges/
COPY ./igworker/src/ ./

CMD [ "python", "app.py" ]
