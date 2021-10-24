from flask import Flask, config, make_response, render_template, request
from flask import url_for, redirect, flash, jsonify
import logging
import os, sys
import json
#from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
sys.path.append(os.path.realpath('.'))
from sexpackges.service.igService import IgService
from sexpackges.service.fbService import FbService
from sexpackges.config import Config

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
    render_data = [
        
    ]
    return render_template('index.html', 
        POST_DELAY=_config.post_delay, 
        Message=message, 
        SLEEP_HOUR_BEGING=_config.sleep_hour_beging, 
        SLEEP_HOUR_END=_config.sleep_hour_end, 
        FB_TOKEN_EXPIRE= _config.fb_token_expire)


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
    
    global _config
    _config = Config("sexsexder-web")
    logging.info(f"Load environment variables:\n{_config.ToString()}")

    global igService
    igService = IgService(_config.sqlite_path, _config.ig_username, _config.ig_session_file, _config.ig_download_folder, _config.max_retry_times)

    global fbService
    fbService = FbService(_config.sqlite_path, _config.fb_page_id, _config.fb_group_id, _config.fb_access_token, _config.max_retry_times)
    
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True, host="0.0.0.0")