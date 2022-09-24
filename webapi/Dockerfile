FROM python:3.8-slim-buster

WORKDIR /app

COPY ./webapi/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#EXPOSE 5000

COPY ./sexpackges/ ./sexpackges/
COPY ./webapi/src/ ./

#CMD ["flask", "run"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
