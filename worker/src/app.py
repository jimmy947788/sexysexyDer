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
import time
import requests
import json
import urllib.parse
import sqlite3
import datetime

def ig_downloader(url):
    try:
        regex = re.compile(r'^(?:https?:\/\/)?(?:www\.)?(?:instagram\.com.*\/p\/)([\d\w\-_]+)(?:\/)?(\?.*)?$')
        match = regex.search(url)
        shortcode = match.group(1)
        logging.debug(f"shortcode : {shortcode}")

        post = instaloader.Post.from_shortcode(ig_loader.context, shortcode)

        logging.debug(f"post {shortcode} downlaoding...")
        ig_loader.download_post(post, target=ig_download_folder.split("/")[-1])

        shortcode_folder = os.path.join(ig_download_folder, f"{post.owner_username}/{shortcode}")
        logging.debug(f"check shortcode folder is {shortcode_folder}")
        if not os.path.exists(shortcode_folder):
            os.makedirs(shortcode_folder)

        # 搬移下載檔案到路徑 {IG帳號}/{shortcode}
        logging.debug(f"move file to shortcode folder.")
        for file in os.listdir(ig_download_folder):
            if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
                src = os.path.join(ig_download_folder, file)
                dst = os.path.join(shortcode_folder, file)
                shutil.move(src, dst)
        
        # 刪除影片封面
        logging.debug(f"remove video cover from shortcode folder.")
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
        

def fb_post_photo2page(folder, ig_owner, ig_linker, message):
    try:
        cfg = {
            "page_id" : fb_page_id, 
            "access_token" :  fb_access_token
        }
        graph = facebook.GraphAPI(cfg['access_token'])

        # 出此PO文所有照片
        photo_file_list = glob.glob(f"{folder}/*.jpg")
        if len(photo_file_list) == 0:
            logging.info("this  post  is vidoe")
            return "" # 沒有照片表示這偏文是影片

        photo_id_list = []
        i = 0
        for image_file in photo_file_list:
            with open(image_file, "rb") as photo:
                photo_id = graph.put_photo(photo, album_id=f'{fb_page_id}/photos',published=False)['id']
                photo_id_list.append(photo_id)
            logging.debug(f"upload photo {image_file} and get photo_id: {photo_id}).  {i+1}/{len(photo_file_list)}")
            i+=1

        args=dict()
        args["message"]= f"{message}\n#自動發文機器人\n\n\n{ig_owner} 的IG傳送門 {ig_linker}"
        for photo_id in photo_id_list:
            key="attached_media["+str(photo_id_list.index(photo_id))+"]"
            args[key]="{'media_fbid': '"+photo_id+"'}"

        result = graph.request(path=f'/{fb_page_id}/feed', args=None, post_args=args, method='POST')
        logging.debug(f"post feed to page (result {result})")

        if "id" in result:
            post_id = result["id"].split("_")[1]
            post_url  = f"https://www.facebook.com/{fb_page_id}/posts/{post_id}/"
            logging.debug(f"post_url : {post_url}")
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

def fb_post_video2page(folder, ig_owner, ig_linker, message):
    try:
        title = urllib.parse.quote_plus(f"{ig_owner} 的IG影片")
        description = urllib.parse.quote_plus(f"{message}\n#自動發文機器人\n\n\n{ig_owner} 的IG傳送門 {ig_linker}")
        url = f"https://graph-video.facebook.com/{fb_page_id}/videos?description={description}&title={title}&access_token={fb_access_token}"
        logging.debug(url)

        video_file_list = glob.glob(f"{folder}/*.mp4")
        if len(video_file_list) == 0:
            logging.info("this  post  have no video")
            return list()

        logging.info(f"this post has {len(video_file_list) } videos")

        post_video_urls = list()
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
    
def post_dequeue():
    connection = None
    cursor = None
    try:

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        query_sql = "SELECT * FROM [ig_post] WHERE status <:status ORDER BY create_time ASC limit 1"
        query_data = { "status": 3 } # 0:待發送, 1:粉專發完成 2:社團分享完成, 3:結束
        cursor.execute(query_sql, query_data)

        fetchedData = cursor.fetchone()

        if fetchedData:
            shortcode = fetchedData[0]
            message = fetchedData[1]
            ig_linker = fetchedData[2]
            status = fetchedData[3]
            create_time = fetchedData[4]
            post_time = fetchedData[5]
            return (shortcode, message, ig_linker, status, create_time, post_time)
        else:
            return (None, None, None, None, None, None)

    except Exception as e:
        logging.error("post_dequeue", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_ig_post_status(shortcode):
    connection = None
    cursor = None
    try:

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        query_sql = "SELECT status FROM [ig_post] WHERE shortcode=:shortcode"
        query_data = { "shortcode": shortcode }
        cursor.execute(query_sql, query_data)
        return cursor.fetchone()[0]

    except Exception as e:
        logging.error("get_ig_post_status", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_status(shortcode, status):
    connection = None
    cursor = None
    try:
        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        update_sql = "UPDATE [ig_post]  SET status = ?, post_time=?  WHERE shortcode=?"
        update_data = (status,  datetime.datetime.now(), shortcode)
        cursor.execute(update_sql, update_data)

        # close the cursor and database connection 
        connection.commit()
        
    except Exception as e:
        logging.error("update_status error", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_fb_url(shortcode:str, post_type:int, post_url:str):
    """紀錄發文狀況

    Args:
        shortcode (str): IG文編號
        post_type (int): 1:照片, 2:影片
        post_url (str):  發後網址
    """
    connection = None
    cursor = None
    try:
        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        insert_sql = "INSERT INTO [fb_post] (shortcode, post_type, post_url, isShared) VALUES (?, ?, ?, ?)"
        insert_data = (shortcode, post_type, post_url, False)
        cursor.execute(insert_sql, insert_data)

        # close the cursor and database connection 
        connection.commit()
        
    except Exception as e:
        logging.error("insert_fb_url error", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_fb_post_shared(shortcode:str, post_type:int, post_url:str, isShared:bool = True):
    """更新分享社團欄位

    Args:
        shortcode (str): IG文編號
        post_type (int): 1:照片, 2:影片
        isShared (bool, optional): 是否分享到社團
    """
    connection = None
    cursor = None
    try:
        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        update_sql = "UPDATE [fb_post] SET isShared=? WHERE shortcode=? and post_type=? and post_url=?"
        update_data = (isShared, shortcode, post_type, post_url)
        cursor.execute(update_sql, update_data)

        # close the cursor and database connection 
        connection.commit()
        
    except Exception as e:
        logging.error("update_fb_post_shared error", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def find_fb_posts(shortcode:str, post_type:int):
    """取得FB發文狀態

    Args:
        shortcode (str): IG文編號
        post_type (int): 1:照片, 2:影片

    Returns:
        List: list(shortcode, post_type, post_url, isShared)
    """
    connection = None
    cursor = None
    try:

        # make the database connection with detect_types 
        connection = sqlite3.connect(sqlite_path,
            detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # insert the data into table
        query_sql = "SELECT * FROM [fb_post] WHERE shortcode=:shortcode and post_type=:post_type"
        query_data = { 
            "shortcode": shortcode,  
            "post_type": post_type
        }
        cursor.execute(query_sql, query_data)

        fetchedData = cursor.fetchall()
        return fetchedData

    except Exception as e:
        logging.error("post_dequeue", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    global ig_loader
    global ig_download_folder
    global fb_page_id
    global fb_group_id
    global fb_access_token
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

    while True:
        try:
            (shortcode, message, ig_linker, status, create_time, post_time) = post_dequeue()
            if shortcode:
                logging.info(f"[step.1] Download IG post from  {ig_linker}")
                (ig_owner, shortcode, shortcode_folder) = ig_downloader(ig_linker)


                status= get_ig_post_status(shortcode)
                # 0:待發送, 1:粉專發完成 2:社團分享完成, 3:結束
                if status == 0:
                    logging.info(f"[step.2] Post {shortcode} to FB page")
                    
                    fb_photo_post = find_fb_posts(shortcode, 1)
                    if len(fb_photo_post) ==0:
                        post_photo_url = fb_post_photo2page(shortcode_folder, ig_owner, ig_linker, message)
                        insert_fb_url(shortcode,1, post_photo_url)

                    fb_video_post = find_fb_posts(shortcode, 2)
                    if len(fb_video_post) ==0:
                        post_video_urls = fb_post_video2page(shortcode_folder, ig_owner, ig_linker, message)
                        for post_url in post_video_urls:
                            insert_fb_url(shortcode,2, post_url)

                    update_status(shortcode, 1)

                status= get_ig_post_status(shortcode)
                if status == 1:
                    logging.info(f"[step.3] share {shortcode} to FB Group ")

                    fb_photo_post = find_fb_posts(shortcode, 1)
                    if len(fb_photo_post) > 0:
                        isShared = fb_photo_post[0][3]
                        post_photo_url = fb_photo_post[0][2]
                        if not isShared:
                            fb_share_post2group(post_photo_url)
                            update_fb_post_shared(shortcode, 1, post_photo_url)

                    fb_video_post = find_fb_posts(shortcode, 2)
                    for (_, _, post_url, isShared) in fb_video_post:
                        if not isShared:
                            fb_share_post2group(post_url)
                            update_fb_post_shared(shortcode, 2, post_url)
                        
                    update_status(shortcode, 2)

                update_status(shortcode, 3)
                logging.info(f" **** sleep {post_delay}s fot next post **** ")
                time.sleep(post_delay)
            else:
                logging.info(f"no post in queue, wait 10 seconds ")
                time.sleep(10)
        except Exception as e:
            logging.error(str(e), exc_info=e)
            logging.info(f"have some error, wait 10 seconds ")
            time.sleep(10)
        
        
            