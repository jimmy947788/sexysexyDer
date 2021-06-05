from typing import SupportsComplex
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

        logging.info(f"move downlods file to shortcode folder (path : {shortcode_folder})")
        for file in os.listdir(save_path):
            if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
                src = os.path.join(save_path, file)
                dst = os.path.join(shortcode_folder, file)
                shutil.move(src, dst)
        
        return shortcode_folder

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
        

def fb_post2page(folder, ig_linker):
    try:
        cfg = {
            "page_id" : fb_page_id, 
            "access_token" :  fb_access_token
        }
        graph = facebook.GraphAPI(cfg['access_token'])

        # 上傳圖片
        img_list = glob.glob(f"{folder}/*.jpg")
        imgs_id = []
        i = 0
        for img in img_list:
            photo = open(img, "rb")
            imgs_id.append(graph.put_photo(photo, album_id=f'{fb_page_id}/photos',published=False)['id'])
            photo.close()
            logging.info(f"upload photo { imgs_id[i] }.  {i+1}/{len(img_list)}")
            i+=1

        args=dict()
        args["message"]= f"防疫期間大家在家裡看妹就好\n我們有最強大的\"工人智慧\"每天篩選發文\n如果覺得不錯再幫忙推薦給朋友壯大社群\n#自動發文機器人\n\n\nIG傳送門 {ig_linker}"
        for img_id in imgs_id:
            key="attached_media["+str(imgs_id.index(img_id))+"]"
            args[key]="{'media_fbid': '"+img_id+"'}"

        ret = graph.request(path=f'/{fb_page_id}/feed', args=None, post_args=args, method='POST')
        logging.info(f"post feed to page (result {ret})")

        ids = ret["id"].split("_")
        post_url  = f"https://www.facebook.com/{ids[0]}/posts/{ids[1]}/"
        logging.info(f"post_link : {post_url}")

        return post_url

    except facebook.GraphAPIError as graphAPIError:
        logging.error(graphAPIError.message, graphAPIError)
        raise Exception("post to fb page error")
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

def fb_post2group(post_url):
    try:
        graph = facebook.GraphAPI(access_token=fb_access_token)

        message = "妹不就好棒棒粉絲專業轉發\n#自動發文機器人"
        ret = graph.put_object(fb_group_id,'feed', message=message,link=post_url)
        logging.info(f"post feed to group (result {ret})")

    except facebook.GraphAPIError as graphAPIError:
        if graphAPIError.message != "Unsupported post request.":
            logging.error(graphAPIError.message, graphAPIError)
            raise Exception("post to fb group error")
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
        raise Exception("post to fb group error")

def callback(ch, method, properties, body):
    
    logging.info(f"wait {post_wait_sec}s ")
    time.sleep(post_wait_sec)
    
    ig_linker = body.decode('utf-8') 
    print(" [x] Received %r" % ig_linker)
    logging.info(" [x] Received %r" % ig_linker)

    shortcode_folder = ig_downloader(ig_linker)
    post_url = fb_post2page(shortcode_folder, ig_linker)
    fb_post2group(post_url)



def main():
    try:
        logging.info("sleep 10s waiting container discover rabbitmq")
        print("sleep 10s waiting container discover rabbitmq")
        time.sleep(10)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('MQ_HOST')))
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        logging.info(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except pika.exceptions.StreamLostError as streamLostError:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
QUEUE_NAME="sexsexder"
if __name__ == '__main__':
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.basicConfig(filename='./logs/sexsexder.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    load_dotenv() 

    global  id_username
    global  ig_session_file
    global  fb_page_id
    global  fb_group_id
    global  fb_access_token
    global  post_wait_sec

    id_username= os.getenv('IG_USERNAME')
    ig_session_file=  os.getenv('IG_SESSION_FILE')
    fb_page_id = os.getenv('FB_PAGE_ID')
    fb_group_id = os.getenv('FB_GROUP_ID')
    fb_access_token= os.getenv('FB_ACCESS_TOKEN')
    post_wait_sec = int(os.getenv('PSOT_WAIT_SEC'))

    environment_mesg = "read environment :"
    environment_mesg += f"id_username={id_username}, "
    environment_mesg += f"ig_session_file={ig_session_file}, "
    environment_mesg += f"fb_page_id={fb_page_id}, "
    environment_mesg += f"fb_group_id={fb_group_id}, "
    environment_mesg += f"fb_access_token={fb_access_token} "
    logging.info(environment_mesg)

    main()