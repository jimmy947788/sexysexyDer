import os
import sys
import glob
from pathlib import Path
import shutil
import traceback
import os
from dotenv import load_dotenv
import logging
import time
import datetime
sys.path.append(os.path.realpath('.'))
from sexpackges.service.igService import IgService
from sexpackges.service.fbService import FbService

if __name__ == '__main__':
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
    log_file = os.path.join(log_folder, 'worker-fbposter.log')
    if log_level.upper() == "DEBUG":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(filename=log_file, level=log_level, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [worker]: %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info(env_text)


    igService = IgService(sqlite_path, id_username, ig_session_file, ig_download_folder)
    fbService = FbService(sqlite_path, fb_page_id, fb_group_id, fb_access_token)
    while True:
        try:
            hours_added = datetime.timedelta(hours = 8)
            now = datetime.datetime.now() + hours_added
            logging.info(f"===============> date time now : {now}")
            sleepBeging = now.replace(hour=sleep_hour_beging, minute=0, second=0, microsecond=0)
            sleepEnd = now.replace(hour=sleep_hour_end, minute=0, second=0, microsecond=0)
            if sleepBeging <= now  and now <= sleepEnd :
                logging.info(f"===============> not in work time range. ({sleepBeging} ~ {sleepEnd})")
            else:
                status_filter = [-1, 0, 1, 2]  #-1:失敗放棄, 0:新資料, 
                for fb_model in fbService.FindAll(status_filter):
                    if fb_model.status ==0: # 準備要上傳FB粉專

                        if fb_model.type == 1: #照片
                            fb_model.retry += 1
                            fbService.Edit(fb_model)
                            logging.info(f"[step.1] Post photo to FB page {fb_model.shortcode} ")

                            ig_model =igService.Find(fb_model.shortcode)
                            photosFiles = fb_model.files
                            owner = ig_model.owner
                            ig_linker = ig_model.link
                            message = fb_model.message
                            fb_model.retry += 1
                            fb_model.link = fbService.PostPhotos(photosFiles, owner, ig_linker, message )
                            fb_model.status = 1
                            fb_model.retry = 0
                            fbService.Edit(fb_model)
                            logging.info(f"====== update new FB model:  {fb_model.ToString()}" )
                        
                        elif  fb_model.type == 2: #影片
                            fb_model.retry += 1
                            fbService.Edit(fb_model)
                            logging.info(f"[step.1] Post Video to FB page {fb_model.shortcode} ")

                            ig_model =igService.Find(fb_model.shortcode)
                            videoFile = fb_model.files[0]
                            owner = ig_model.owner
                            ig_linker = ig_model.link
                            message = fb_model.message
                            fb_model.link = fbService.PostVideo(videoFile, owner, ig_linker, message )
                            fb_model.status = 1
                            fb_model.retry = 0
                            fbService.Edit(fb_model)
                            logging.info(f"====== update new FB model:  {fb_model.ToString()}" )
                    
                    elif fb_model.status ==1: # 準備分享到社團
                        fb_model.retry += 1
                        fbService.Edit(fb_model)
                        
                        logging.info(f"[step.2] Shared photo to FB Group {fb_model.shortcode} ")
                        logging.info(f"===============>link: {fb_model.link}")
                        fbService.ShareToGroup(fb_model.link )
                        
                        fb_model.status = 2
                        fbService.Edit(fb_model)

        except Exception as e:
            logging.error(str(e), exc_info=e)
            logging.info(f"have some error, wait 10 seconds ")
        finally:
            logging.info(f" **** sleep {post_delay}s for next post **** ")
            time.sleep(post_delay)
        
        
            