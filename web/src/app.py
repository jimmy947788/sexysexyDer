from flask import Flask
from flask import render_template
from flask import request
import logging
import os
import pika

app = Flask(__name__)
QUEUE_NAME="sexsexder"


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    msg1 = ""
    msg2  = ""
    post_linker = ""
    if request.method == 'POST':
        if request.form.get('txt_ig_linker'): 
            post_linker = request.form.get('txt_ig_linker')

            connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('MQ_HOST')))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=post_linker)

    return render_template('index.html', message=msg1, post_linker=post_linker, error_message=msg2)

if __name__ == "__main__":

    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.basicConfig(filename='./logs/sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    
    #credentials = pika.PlainCredentials('guest', 'guest')
    #parameters = pika.ConnectionParameters('rabbitmq', 5672,'/',credentials)
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters("192.168.0.105"))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    """

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')