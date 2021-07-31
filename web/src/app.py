from flask import Flask, make_response, render_template, request
from flask import url_for, redirect, flash, jsonify
import logging
import os, sys
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import re
import datetime
import sqlite3
  

app = Flask(__name__)


def response_json(obj):
    #response = make_response( jsonify(obj), 200)
    #response.mimetype = 'application/json'
    #return response
    return jsonify(obj)

def findShortcode(url):
    regex = re.compile(r'^(?:https?:\/\/)?(?:www\.)?(?:instagram\.com.*\/p\/)([\d\w\-_]+)(?:\/)?(\?.*)?$')
    match = regex.search(url)
    shortcode = match.group(1)
    return shortcode

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
    return render_template('index.html', POST_DELAY=post_delay, Message=message)


@app.route('/delete_post', methods=['POST'])
def delete_post():
    connection = None
    cursor = None
    try:
        if not request.values.get('shortcode'):
            raise Exception("必須提供shortcode")
        
        shortcode = request.form.get('shortcode')
        logging.info(f"delete post shortcode : {shortcode}")

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        delete_sql = "DELETE FROM [ig_post]  WHERE shortcode=?"
        delete_data = (shortcode, )
        cursor.execute(delete_sql, delete_data)

        # close the cursor and database connection 
        connection.commit()
        
        result = {
            "isSuccess": True,
            "message" : None,
            "data" : None
        }
    except Exception as e:
        logging.error("call delete_post failed", exc_info=e)
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

    return response_json(result)

def check_shortcode_exist(shortcode):
    connection = None
    cursor = None
    try:

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        query_sql = "SELECT COUNT(*) FROM [ig_post] WHERE shortcode=?"
        query_data = (shortcode, )
        cursor.execute(query_sql, query_data)

        fetchedData = cursor.fetchone()

        return int(fetchedData[0]) >=1
    except Exception as e:
        logging.error("call check_shortcode_exist failed", exc_info=e)
        raise Exception("check_shortcode_exist error", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/get_posts', methods=['GET'])
def get_posts():
    connection = None
    cursor = None
    try:

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        query_sql = "SELECT * FROM [ig_post] WHERE status <:status ORDER BY create_time ASC"
        query_data = { "status": 3 } # 0:待發送, 1:粉專發完成 2:社團分享完成, 3:結束
        cursor.execute(query_sql, query_data)
        fetchedData = cursor.fetchall()
        
        query_sql = "SELECT COUNT(*) FROM [ig_post] WHERE status <:status"
        query_data = { "status": 3 } # 0:待發送, 1:粉專發完成 2:社團分享完成, 3:結束
        cursor.execute(query_sql, query_data)
        totals = cursor.fetchone()[0]

        result = {
            "isSuccess": True,
            "message" : None,
            "data" : fetchedData,
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

    return response_json(result)

@app.route('/add_post', methods=['POST'])
def add_post():

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

        if check_shortcode_exist(shortcode):
            raise Exception(f"{shortcode} 已經排入發送")

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        insert_sql = "INSERT INTO [ig_post] (shortcode, message, ig_linker, status, create_time, post_time) VALUES ( ?, ?, ?, ?, ?, ?)"
        insert_data = (shortcode, message, igLinker, 0, datetime.datetime.now(), datetime.datetime.now())
        cursor.execute(insert_sql, insert_data)

        # close the cursor and database connection 
        connection.commit()
        
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

    return response_json(result)

if __name__ == "__main__":
    global post_delay
    global sqlite_path

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