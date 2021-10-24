import os
import sys
import os
from dotenv import load_dotenv
import logging
import time
from multiprocessing.pool import ThreadPool
sys.path.append(os.path.realpath('.'))
from sexpackges.service.igService import IgService
from sexpackges.service.fbService import FbService

def download_completed(shortcode:str, owner:str, folder:str, photos:list, videos:list, errMsg:str):
    
    ig_model = igService.Find(shortcode)
    if errMsg: 
        logging.info(f"====== download {shortcode} was falied, error message : {errMsg} ")
        ig_model.status = -1
    else:
        logging.info(f"====== download {shortcode}  was success,  get photos({len(photos)}) amd videos ({len(videos)})")
        ig_model.owner = owner
        ig_model.status = 1
        ig_model.save_path = folder
      
        if len(photos) >= 1:
            logging.info(f"======download photos list : { ','.join(photos) }")
            fbService.Add(shortcode, 1, ig_model.message, ','.join(photos))
        
        for videoPath in videos:
            logging.info(f"======download video file : { videoPath }")
            fbService.Add(shortcode, 2, ig_model.message, videoPath)
      
    
    ig_model.retry += 1
    igService.Edit(ig_model)
    logging.info(f"====== update new IG model:  {ig_model.ToString()}" )

if __name__ == '__main__':

    load_dotenv() 
    global igService 
    global fbService

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
    log_file = os.path.join(log_folder, 'worker-igdownloader.log')
    if log_level.upper() == "DEBUG":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(filename=log_file, level=log_level, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [worker]: %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info(env_text)

    try :
        igService = IgService(sqlite_path, id_username, ig_session_file, ig_download_folder)
        fbService = FbService(sqlite_path, fb_page_id, fb_group_id, fb_access_token )
        while True:
            try:
                
                status_filter = [-1, 0]  #-1:失敗放棄, 0:新資料, 
                shortcodes = []
                for post in  igService.FindAll(status_filter):
                    shortcodes.append(post.shortcode)

                threadCount =  len(shortcodes)

                if threadCount > 0:
                    logging.info(f"====== create { threadCount }  thread  download post file")
                    # Run 5 multiple threads. Each call will take the next element in urls list
                    for  (shortcode, owner, folder ,photos, videos, errMsg) in  ThreadPool(threadCount).imap_unordered(igService.Download, shortcodes):
                        download_completed (shortcode, owner, folder, photos, videos, errMsg) 

            except Exception as e:
                logging.error(str(e), exc_info=e)
                logging.info(f"have some error, wait 10 seconds ")
            finally:
                logging.info(f" **** sleep {post_delay}s for next post **** ")
                time.sleep(post_delay)
    except Exception as e:
            logging.error(str(e), exc_info=e)
            logging.info(f"have some error, wait 10 seconds ")
        
        