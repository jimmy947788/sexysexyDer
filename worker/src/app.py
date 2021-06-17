from typing import SupportsComplex

from requests.sessions import extract_cookies_to_jar
import facebook
import instaloader 
import os
import sys
import re
import glob
from pathlib import Path
import shutil
import traceback
import os
from dotenv import load_dotenv
import logging
import pika
import time
import requests
import json
import urllib.parse

def ig_downloader(url):
    try:
        regex = re.compile(r'^(?:https?:\/\/)?(?:www\.)?(?:instagram\.com.*\/p\/)([\d\w\-_]+)(?:\/)?(\?.*)?$')
        match = regex.search(url)
        shortcode = match.group(1)
        logging.info(f"shortcode : {shortcode}")

        post = instaloader.Post.from_shortcode(ig_loader.context, shortcode)

        logging.info(f"post {shortcode} downlaoding...")
        ig_loader.download_post(post, target=ig_download_folder.split("/")[-1])

        shortcode_folder = os.path.join(ig_download_folder, f"{post.owner_username}/{shortcode}")
        logging.info(f"check shortcode folder is {shortcode_folder}")
        if not os.path.exists(shortcode_folder):
            os.makedirs(shortcode_folder)

        # 搬移下載檔案到路徑 {IG帳號}/{shortcode}
        logging.info(f"move file to shortcode folder.")
        for file in os.listdir(ig_download_folder):
            if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
                src = os.path.join(ig_download_folder, file)
                dst = os.path.join(shortcode_folder, file)
                shutil.move(src, dst)
        
        # 刪除影片封面
        logging.info(f"remove video cover from shortcode folder.")
        video_file_list = glob.glob(f"{shortcode_folder}/*.mp4")
        for video_file in video_file_list:
            image_file = video_file.replace(".mp4", ".jpg")
            os.remove(image_file)

        return (post.owner_username, shortcode, shortcode_folder)

    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        logging.error(errMsg,e)
        raise Exception("Download IG post has error")
        

def fb_post_photo2page(folder, ig_owner, ig_linker):
    try:
        cfg = {
            "page_id" : fb_page_id, 
            "access_token" :  fb_access_token
        }
        graph = facebook.GraphAPI(cfg['access_token'])

        # 出此PO文所有照片
        photo_file_list = glob.glob(f"{folder}/*.jpg")
        if len(photo_file_list) == 0:
            return "" # 沒有照片表示這偏文是影片

        photo_id_list = []
        i = 0
        for image_file in photo_file_list:
            with open(image_file, "rb") as photo:
                photo_id = graph.put_photo(photo, album_id=f'{fb_page_id}/photos',published=False)['id']
                photo_id_list.append(photo_id)
            logging.info(f"upload photo {image_file} and get photo_id: {photo_id}).  {i+1}/{len(photo_file_list)}")
            i+=1

        args=dict()
        args["message"]= f"防疫期間大家在家裡看妹就好\n我們有最強大的\"工人智慧\"每天篩選發文\n如果覺得不錯再幫忙推薦給朋友壯大社群\n#自動發文機器人\n\n\n{ig_owner} 的IG傳送門 {ig_linker}"
        for photo_id in photo_id_list:
            key="attached_media["+str(photo_id_list.index(photo_id))+"]"
            args[key]="{'media_fbid': '"+photo_id+"'}"

        result = graph.request(path=f'/{fb_page_id}/feed', args=None, post_args=args, method='POST')
        logging.info(f"post feed to page (result {result})")

        if "id" in result:
            post_id = result["id"].split("_")[1]
            post_url  = f"https://www.facebook.com/{fb_page_id}/posts/{post_id}/"
            logging.info(f"post_url : {post_url}")
            return post_url

        if "error" in result:
            message = result["error"]["message"]
            raise Exception(message)

    except facebook.GraphAPIError as graphAPIError:
        logging.error(graphAPIError.message, graphAPIError)
        raise Exception("post images to FB page error")
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        logging.error(errMsg,e)
        raise Exception("post images to FB page error")

def fb_post_video2page(folder, ig_owner, ig_linker):
    try:
        title = urllib.parse.quote_plus(f"{ig_owner} 的IG影片")
        description = urllib.parse.quote_plus(f"防疫期間大家在家裡看妹就好\n我們有最強大的\"工人智慧\"每天篩選發文\n如果覺得不錯再幫忙推薦給朋友壯大社群\n#自動發文機器人\n\n\n{ig_owner} 的IG傳送門 {ig_linker}")
        url = f"https://graph-video.facebook.com/{fb_page_id}/videos?description={description}&title={title}&access_token={fb_access_token}"
        logging.debug(url)

        video_file_list = glob.glob(f"{folder}/*.mp4")
        post_video_urls = []
        for video_file in video_file_list:
            logging.debug(f"post video_file={video_file}") 
            files = {'file': open(video_file, 'rb')}
            response = requests.post(url, files=files)
            logging.debug(f"response: {response.text}")
            result = json.loads(response.text)

            if "id" in result:
                postId = result["id"] 
                post_video_urls.append(f"https://www.facebook.com/sexysexyDer/videos/{postId}")
            if "error" in result:
                message = result["error"]["message"]
                raise Exception(message)
        return post_video_urls

    except facebook.GraphAPIError as graphAPIError:
        logging.error(graphAPIError.message, graphAPIError)
        raise Exception("post video to FB page error")
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        logging.error(errMsg,e)
        raise Exception("post to fb page error")

def fb_share_post2group(post_url):
    try:
        graph = facebook.GraphAPI(access_token=fb_access_token)

        message = "#轉發 #自動發文機器人"
        ret = graph.put_object(fb_group_id,'feed', message=message,link=post_url)
        logging.info(f"share post to group (result {ret})")

    except facebook.GraphAPIError as graphAPIError:
        if graphAPIError.message != "Unsupported post request.":
            logging.info(graphAPIError.message)
            logging.error(graphAPIError.message, graphAPIError)
            raise Exception("share post to group error")
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        logging.error(errMsg,e)
        raise Exception("share post to group error")

def callback(ch, method, properties, body):
    ig_linker = body.decode('utf-8') 
    logging.info(" [x] Received %r" % ig_linker)
    try:
        (ig_owner, shortcode, shortcode_folder) = ig_downloader(ig_linker)
        post_url = fb_post_photo2page(shortcode_folder, ig_owner, ig_linker)
        if post_url:
            logging.info(f"post_url: {post_url}")
            logging.info(f"share {shortcode} photos to FB Group after {post_delay}s")
            time.sleep(post_delay)
            fb_share_post2group(post_url)

        post_video_urls = fb_post_video2page(shortcode_folder, ig_owner, ig_linker)
        for post_url in post_video_urls:
            logging.info(f"post_url: {post_url}")
            logging.info(f"share {shortcode} video to FB Group after {post_delay}s")
            time.sleep(post_delay)
            fb_share_post2group(post_url)
    except Exception as e:
        logging.error("consuming error", e)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    

if __name__ == '__main__':
    global ig_loader
    global ig_download_folder
    global fb_page_id
    global fb_group_id
    global fb_access_token
    global post_delay
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
    log_file = os.path.join(log_folder, 'sexsexder-worker.log')
    if log_level.upper() == "DEBUG":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(filename=log_file, level=log_level, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [worker]: %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info(env_text)

    # Get instance
    ig_loader = instaloader.Instaloader()
    ig_loader.load_session_from_file(id_username, ig_session_file) 
    logging.info(f"create ig_loader from IG session file.")

    credentials = pika.PlainCredentials(mq_user, mq_pass)
    parameters = pika.ConnectionParameters(host=mq_host, port=mq_port, credentials=credentials, heartbeat=0)
    connection = pika.BlockingConnection(parameters)
    logging.info(f"connect to rabbitMQ...")

    channel = connection.channel()
    channel.queue_declare(queue=mq_name)
    channel.basic_consume(queue=mq_name, on_message_callback=callback, auto_ack=False)
    
    logging.info(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()