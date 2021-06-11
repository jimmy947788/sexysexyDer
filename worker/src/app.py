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
        logging.info(f"get shortcode : {shortcode}")

        # Get instance
        L = instaloader.Instaloader()
        L.load_session_from_file(id_username, ig_session_file) # (load session created w/
        #L.login(username, password)        # (login)
        #L.interactive_login(username)      # (ask password on terminal)

        post = instaloader.Post.from_shortcode(L.context, shortcode)
        #print(f"owner_username={post.owner_username}")
        save_path = "downloads" #os.path.join("downloads", f"{post.owner_username}-{shortcode}")
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        logging.info(f"IG post downlaod now... ( shortcode: {shortcode})")
        L.download_post(post, target=save_path)

        shortcode_folder = f"downloads/{post.owner_username}/{shortcode}"
        if not os.path.exists(shortcode_folder):
            os.makedirs(shortcode_folder)

        # 搬移下載檔案到路徑 {IG帳號}/{shortcode}
        logging.info(f"move downlods file to shortcode folder (path : {shortcode_folder})")
        for file in os.listdir(save_path):
            if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
                src = os.path.join(save_path, file)
                dst = os.path.join(shortcode_folder, file)
                shutil.move(src, dst)
        
        # 刪除影片封面
        logging.info(f"remove video cover from shortcode folder (path : {shortcode_folder})")
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
    
    
QUEUE_NAME="sexsexder"
if __name__ == '__main__':
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.basicConfig(filename='./logs/sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [worker]: %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    load_dotenv() 

    global  id_username
    global  ig_session_file
    global  fb_page_id
    global  fb_group_id
    global  fb_access_token
    global  post_delay

    mq_host = os.getenv("MQ_HOST")
    mq_user = os.getenv("MQ_USER")
    mq_pass = os.getenv("MQ_PASS")
    post_delay = int(os.getenv("POST_DELAY"))
    id_username= os.getenv('IG_USERNAME')
    ig_session_file=  os.getenv('IG_SESSION_FILE')
    fb_page_id = os.getenv('FB_PAGE_ID')
    fb_group_id = os.getenv('FB_GROUP_ID')
    fb_access_token= os.getenv('FB_ACCESS_TOKEN')

    environment_mesg = "read environment :"
    environment_mesg += f"id_username={id_username}, "
    environment_mesg += f"ig_session_file={ig_session_file}, "
    environment_mesg += f"fb_page_id={fb_page_id}, "
    environment_mesg += f"fb_group_id={fb_group_id}, "
    environment_mesg += f"fb_access_token={fb_access_token}, "
    environment_mesg += f"mq_host={mq_host} "
    environment_mesg += f"post_delay={post_delay} "
    logging.info(environment_mesg)

    logging.info(f"MQ_HOST={mq_host}, MQ_USER={mq_user}, MQ_PASS={mq_pass}")
    credentials = pika.PlainCredentials(mq_user, mq_pass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(mq_host, heartbeat=0, credentials=credentials))
    logging.info(f"connect to rabbitMQ...")

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    logging.info(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()