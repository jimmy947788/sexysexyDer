FROM python:3.8-slim-buster

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY ../sexpackges/ ./
COPY src/ ./

#CMD ["flask", "run"]
CMD [ "python", "app.py" ]