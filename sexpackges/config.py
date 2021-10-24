import os
import sys
import logging
from dotenv import load_dotenv

class Config(object):
    def __init__(self, appname):
        load_dotenv() 
    
        self.sqlite_path = os.getenv("SQLITE_PATH")
        self.post_delay = int(os.getenv("POST_DELAY"))
        self.ig_username= os.getenv('IG_USERNAME')
        self.ig_session_file = os.getenv('IG_SESSION_FILE')
        self.ig_download_folder = os.getenv("IG_DOWNLOAD_FOLDER")
        self.fb_page_id = os.getenv('FB_PAGE_ID')
        self.fb_group_id = os.getenv('FB_GROUP_ID')
        self.fb_access_token= os.getenv('FB_ACCESS_TOKEN')
        self.fb_token_expire= os.getenv('FB_TOKEN_EXPIRE')
        self.log_folder = os.getenv('LOG_FOLDER')
        self.log_level = os.getenv('LOG_LEVEL')
        self.sleep_hour_beging = int(os.getenv('SLEEP_HOUR_BEGING')) #不發文開始小時(24小時制)
        self.sleep_hour_end = int(os.getenv('SLEEP_HOUR_END')) #不發文結束小時(24小時制)
        self.max_retry_times = 5
        self._initLog(appname)

    def _initLog(self, name):
        if not os.path.exists(self.log_folder):
                os.makedirs(self.log_folder)

        log_file = os.path.join(self.log_folder, name + '.log')
        
        if self.log_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        
        logging.basicConfig(filename=log_file, level=log_level, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s [worker]: %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    def ToString(self):
        env_text = f"SQLITE_PATH={self.sqlite_path}\n"
        env_text += f"\tPOST_DELAY={self.post_delay}\n"
        env_text += f"\tIG_USERNAME={self.ig_username}\n "
        env_text += f"\tIG_SESSION_FILE={self.ig_session_file}\n"
        env_text += f"\tIG_DOWNLOAD_FOLDER={self.ig_download_folder}\n"
        env_text += f"\tFB_PAGE_ID={self.fb_page_id}\n"
        env_text += f"\tFB_GROUP_ID={self.fb_group_id}\n"
        env_text += f"\tFB_ACCESS_TOKEN={self.fb_access_token}\n"
        env_text += f"\tLOG_FOLDER={self.log_folder}\n"
        env_text += f"\tLOG_LEVEL={self.log_level}\n"
        env_text += f"\tSLEEP_HOUR_BEGING={self.sleep_hour_beging}\n"
        env_text += f"\tSLEEP_HOUR_END={self.sleep_hour_end}\n"
        return env_text