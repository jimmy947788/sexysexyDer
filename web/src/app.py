from flask import Flask, make_response, render_template, request
from flask import url_for, redirect, flash, jsonify
import logging
import os, sys
import json
from dotenv import load_dotenv
#from requests.auth import HTTPBasicAuth
import datetime
from urllib.parse import urlparse
sys.path.append(os.path.realpath('.'))
from sexpackges.service.igService import IgService

app = Flask(__name__)

def findShortcode(url):
    u = urlparse(url)
    #print(u)
    #print(f"path : {u.path}")
    # path =/reel/CR_QcmBBlQ2/
    # path =/p/CR_QcmBBlQ2/
    return u.path.split('/')[-2:-1][0]

@app.route('/login', methods=['GET', 'POST'])
def login():
    #if request.method == 'GET':
    #    return render_template("login.html")
    
    # request.form['user_id'
    return render_template('login.html')

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    message = f"防疫期間大家在家裡看妹就好\n我們有最強大的\"工人智慧\"每天篩選發文\n如果覺得不錯再幫忙推薦給朋友壯大社群"
    return render_template('index.html', POST_DELAY=post_delay, Message=message, SLEEP_HOUR_BEGING=sleep_hour_beging, SLEEP_HOUR_END=sleep_hour_end)


@app.route('/delete', methods=['POST'])
def delete():
    connection = None
    cursor = None
    try:
        if not request.values.get('shortcode'):
            raise Exception("必須提供shortcode")
        
        shortcode = request.form.get('shortcode')
        logging.info(f"delete post shortcode : {shortcode}")

        igService.Remove(shortcode)
        
        result = {
            "isSuccess": True,
            "message" : None,
            "data" : None
        }
    except Exception as e:
        logging.error("call delete failed", exc_info=e)
        result = {
            "isSuccess": False,
            "message" : str(e),
            "data" : None
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return jsonify(result)

@app.route('/listall', methods=['GET'])
def list_all():
    connection = None
    cursor = None
    try:

        data = igService.FindAll()
        totals = len(data)

        json_string = json.dumps(data, default=lambda o: o.__dict__) #, indent=4)
        logging.debug(json_string)
        result = {
            "isSuccess": True,
            "message" : None,
            "data" :  json_string,
            "totals" : totals
        }
    except Exception as e:
        logging.error("call get_posts failed", exc_info=e)
        result = {
            "isSuccess": False,
            "message" : str(e),
            "data" : None
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return jsonify(result)

@app.route('/add', methods=['POST'])
def add():

    connection = None
    cursor = None
    try:
        if not request.values.get('igLinker'):
            raise Exception("必須提供IG連結")
        
        igLinker = request.form.get('igLinker')
        message = request.form.get('message')
        shortcode = findShortcode(igLinker)
        print(f"igLinker={igLinker}, message={message}, shortcode={shortcode}")
        if not shortcode:
            raise Exception("提供IG連結找不到shortcode")

        logging.info(f"shortcode : {shortcode}")

        if igService.Exists(shortcode):
            raise Exception(f"{shortcode} 已經排入發送")

        igService.Add(shortcode, igLinker, message)
        
        result = {
            "isSuccess": True,
            "message" : None,
            "data" : None
        }
    except Exception as e:
        result = {
            "isSuccess": False,
            "message" : str(e),
            "data" : None
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return jsonify(result)

if __name__ == "__main__":
    global post_delay
    global sleep_hour_beging
    global sleep_hour_end
    global igService

    load_dotenv() 
    
    sqlite_path = os.getenv("SQLITE_PATH")
    post_delay = int(os.getenv("POST_DELAY"))
    id_username= os.getenv('IG_USERNAME')
    ig_session_file = os.getenv('IG_SESSION_FILE')
    ig_download_folder = os.getenv("IG_DOWNLOAD_FOLDER")
    fb_page_id = os.getenv('FB_PAGE_ID')
    fb_group_id = os.getenv('FB_GROUP_ID')
    fb_access_token= os.getenv('FB_ACCESS_TOKEN')
    log_folder = os.getenv('LOG_FOLDER')
    log_level = os.getenv('LOG_LEVEL')
    sleep_hour_beging = int(os.getenv('SLEEP_HOUR_BEGING')) #不發文開始小時(24小時制)
    sleep_hour_end = int(os.getenv('SLEEP_HOUR_END')) #不發文結束小時(24小時制)

    env_text = "Load environment variables:\n"
    env_text += f"SQLITE_PATH={sqlite_path}\n"
    env_text += f"\tPOST_DELAY={post_delay}\n"
    env_text += f"\tIG_USERNAME={id_username}\n "
    env_text += f"\tIG_SESSION_FILE={ig_session_file}\n"
    env_text += f"\tIG_DOWNLOAD_FOLDER={ig_download_folder}\n"
    env_text += f"\tFB_PAGE_ID={fb_page_id}\n"
    env_text += f"\tFB_GROUP_ID={fb_group_id}\n"
    env_text += f"\tFB_ACCESS_TOKEN={fb_access_token}\n"
    env_text += f"\tLOG_FOLDER={log_folder}\n"
    env_text += f"\tLOG_LEVEL={log_level}\n"
    env_text += f"\tSLEEP_HOUR_BEGING={sleep_hour_beging}\n"
    env_text += f"\tSLEEP_HOUR_END={sleep_hour_end}\n"

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

    igService = IgService(sqlite_path, id_username, ig_session_file, ig_download_folder)

    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host="0.0.0.0")