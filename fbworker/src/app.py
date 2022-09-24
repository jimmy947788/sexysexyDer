import os
import sys
import logging
import time
import datetime
sys.path.append(os.path.realpath('.'))
from sexpackges.models.enum import FbPostType, Status
from sexpackges.models.fbPost import FbPost
from sexpackges.service.igService import IgService
from sexpackges.service.fbService import FbService
from sexpackges.config import Config


def post_to_fb_page(fb_model:FbPost):
    # 進來先增次數
    fb_model.retry += 1
    fbService.Edit(fb_model)

    ig_model =igService.Find(fb_model.shortcode)
    owner = ig_model.owner
    ig_linker = ig_model.link
    message = fb_model.message
    if fb_model.type == FbPostType.PHOTOS: #影片
        photosFiles = fb_model.files
        fb_model.link = fbService.PostPhotos(photosFiles, owner, ig_linker, message ) 
    else:
        videoFile = fb_model.files[0]
        fb_model.link = fbService.PostVideo(videoFile, owner, ig_linker, message )

    # 發文成功 狀態更新 重試次數歸零
    fb_model.status = Status.FB_POST_TO_PAGE
    fb_model.retry = 0
    fbService.Edit(fb_model)
    logging.info(f"====== update new FB model:  {fb_model.ToString()}" )
    
    # 更新IG那邊的狀態
    ig_model.status = Status.FB_POST_TO_PAGE
    igService.Edit(ig_model)
    logging.info(f"====== update status IG model:  {ig_model.ToString()}" )

def publish_to_fb_goup(fb_model:FbPost):
    # 進來先增次數
    fb_model.retry += 1
    fbService.Edit(fb_model)
    
    logging.info(f"===============>link: {fb_model.link}")
    fbService.ShareToGroup(fb_model.link )
    
    #TODO: 因為 publish_to_groups API 一定會回錯誤，所以要想辦法解決

    # 發文成功 狀態更新 
    fb_model.status = Status.FB_PUBLISH_TO_GROUP
    fbService.Edit(fb_model)
    logging.info(f"====== update new FB model:  {fb_model.ToString()}" )
 
    # 更新IG那邊的狀態
    ig_model =igService.Find(fb_model.shortcode)
    ig_model.status = Status.FB_PUBLISH_TO_GROUP
    igService.Edit(ig_model)
    logging.info(f"====== update status IG model:  {ig_model.ToString()}" )

if __name__ == '__main__':
    global _config
    _config = Config("sexsexder-fbposter")
    logging.info(f"Load environment variables:\n{_config.ToString()}")
   
    igService = IgService(_config.sqlite_path, _config.ig_username, _config.ig_session_file, _config.ig_download_folder, _config.max_retry_times)
    fbService = FbService(_config.sqlite_path, _config.fb_page_id, _config.fb_group_id, _config.fb_access_token, _config.max_retry_times)
    while True:
        try:
            hours_added = datetime.timedelta(hours = 8)
            now = datetime.datetime.now() + hours_added
            logging.info(f"===============> date time now : {now}")
            sleepBeging = now.replace(hour=_config.sleep_hour_beging, minute=0, second=0, microsecond=0)
            sleepEnd = now.replace(hour=_config.sleep_hour_end, minute=0, second=0, microsecond=0)
            if sleepBeging <= now  and now <= sleepEnd :
                logging.info(f"===============> not in work time range. ({sleepBeging} ~ {sleepEnd})")
            else:
                status_filter = [ Status.WAIT, Status.FB_POST_TO_PAGE ] 
                for fb_model in fbService.FindAll(status_filter):
                    
                    if fb_model.retry >= _config.max_retry_times:
                        fb_model.status = Status.FAILED
                        fbService.Edit(fb_model)
                        continue;

                    if fb_model.status == Status.WAIT: # 準備要上傳FB粉專
                        logging.info(f"[step.1] Post to FB page {fb_model.shortcode} ")
                        post_to_fb_page(fb_model)
                    elif fb_model.status == Status.FB_POST_TO_PAGE: # 準備分享到社團
                        logging.info(f"[step.2] Shared photo to FB Group {fb_model.shortcode} ")
                        publish_to_fb_goup(fb_model)
                       

        except Exception as e:
            logging.error(str(e), exc_info=e)
            logging.info(f"have some error, wait 10 seconds ")
        finally:
            logging.info(f" **** sleep {_config.post_delay}s for next post **** ")
            time.sleep(_config.post_delay)
        
        
            