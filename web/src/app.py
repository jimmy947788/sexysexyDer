from flask import Flask, make_response, render_template, request
import logging
import os, sys
import pika
import time
from dotenv import load_dotenv

app = Flask(__name__)
QUEUE_NAME="sexsexder"


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('txt_ig_linker'): 
            post_linker = request.form.get('txt_ig_linker')
            channel = connection.channel()
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=post_linker)

    return render_template('index.html', POST_WAIT_SEC=post_wait_sec)

@app.route('/GetWaitMessageCount', methods=['GET'])
def getWaitMessageCount():
    channel = connection.channel()
    queue = channel.queue_declare(queue=QUEUE_NAME)
    count = str(queue.method.message_count)
    response = make_response(count, 200)
    response.mimetype = "text/plain"
    return response

if __name__ == "__main__":

    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.basicConfig(filename='./logs/sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [web]: %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    global connection
    logging.info("sleep 10s waiting container discover rabbitmq")
    time.sleep(10)

    load_dotenv() 
    mqHost = os.getenv("MQ_HOST")
    global post_wait_sec
    post_wait_sec = int(os.getenv('POST_WAIT_SEC'))
    logging.info(f"mqHost={mqHost }")
    connection = pika.BlockingConnection(pika.ConnectionParameters(mqHost, heartbeat=0))
    
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')