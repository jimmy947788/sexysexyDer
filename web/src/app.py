from flask import Flask, make_response, render_template, request
import logging
import os, sys
import pika
import time
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('txt_ig_linker'): 
            post_linker = request.form.get('txt_ig_linker')

            credentials = pika.PlainCredentials(mq_user, mq_pass)
            parameters = pika.ConnectionParameters(host=mq_host, port=mq_port, credentials=credentials, heartbeat=20*60) 
            connection = pika.BlockingConnection(parameters)
            logging.debug("connect to rabbitMQ...")
            channel = connection.channel()

            logging.debug("publish message to rabbitMQ...")
            channel.basic_publish(exchange='', routing_key=mq_name, body=post_linker)

            logging.debug("close connect to rabbitMQ...")
            connection.close()

    return render_template('index.html', POST_DELAY=post_delay)

@app.route('/GetWaitMessageCount', methods=['GET'])
def getWaitMessageCount():    
    mq_api_url = f'http://{mq_host}:{mq_web_host}/api/queues/'
    logging.debug(f"URL: {mq_api_url}")
    response = requests.get(mq_api_url, auth=HTTPBasicAuth(mq_user, mq_pass))

    count = "-1"
    if response.status_code == 200:
        logging.debug(response.text)
        jsonObj = json.loads(response.text)
        count = str(jsonObj[0]["messages"])

    response = make_response(count, 200)
    response.mimetype = "text/plain"
    return response

if __name__ == "__main__":
    global connection
    global post_delay
    global mq_host
    global mq_web_host
    global mq_user
    global mq_pass
    global mq_name

    load_dotenv() 
    
    mq_host = os.getenv("MQ_HOST")
    mq_port = int(os.getenv("MQ_PORT"))
    mq_web_host = int(os.getenv("MQ_WEB_PORT"))
    mq_name = os.getenv("MQ_NAME")
    mq_user = os.getenv("RABBITMQ_DEFAULT_USER")
    mq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")
    post_delay = int(os.getenv("POST_DELAY"))
    id_username= os.getenv('IG_USERNAME')
    ig_session_file = os.getenv('IG_SESSION_FILE')
    ig_download_folder = os.getenv("IG_DOWNLOAD_FOLDER")
    fb_page_id = os.getenv('FB_PAGE_ID')
    fb_group_id = os.getenv('FB_GROUP_ID')
    fb_access_token= os.getenv('FB_ACCESS_TOKEN')
    log_folder = os.getenv('LOG_FOLDER')
    log_level = os.getenv('LOG_LEVEL')

    env_text = "Load environment variables:\n"
    env_text += f"\tMQ_HOST={mq_host}\n"
    env_text += f"\tMQ_PORT={mq_port}\n"
    env_text += f"\tMQ_WEB_PORT={mq_web_host}\n"
    env_text += f"\tMQ_NAME={mq_name}\n"
    env_text += f"\tMQ_USER={mq_user}\n"
    env_text += f"\tMQ_PASS={mq_pass}\n"
    env_text += f"\tPOST_DELAY={post_delay}\n"
    env_text += f"\tIG_USERNAME={id_username}\n "
    env_text += f"\tIG_SESSION_FILE={ig_session_file}\n"
    env_text += f"\tIG_DOWNLOAD_FOLDER={ig_download_folder}\n"
    env_text += f"\tFB_PAGE_ID={fb_page_id}\n"
    env_text += f"\tFB_GROUP_ID={fb_group_id}\n"
    env_text += f"\tFB_ACCESS_TOKEN={fb_access_token}\n"
    env_text += f"\tLOG_FOLDER={log_folder}\n"
    env_text += f"\tLOG_LEVEL={log_level}\n"

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    log_file = os.path.join(log_folder, 'sexsexder-web.log')
    if log_level.upper() == "DEBUG":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(filename=log_file, level=log_level, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [worker]: %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info(env_text)

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host="0.0.0.0")