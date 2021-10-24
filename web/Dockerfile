FROM python:3.8-slim-buster

WORKDIR /usr/app

COPY web/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY sexpackges/ ./sexpackges/
COPY web/src/ ./

#CMD ["flask", "run"]
CMD [ "python", "app.py" ]