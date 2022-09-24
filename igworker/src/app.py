import os
import sys
import logging
import time
from multiprocessing.pool import ThreadPool
sys.path.append(os.path.realpath('.'))
from sexpackges.service.igService import IgService
from sexpackges.service.fbService import FbService
from sexpackges.config import Config
from sexpackges.models.enum import Status, FbPostType

"""
def download_completed(shortcode:str, owner:str, folder:str, photos:list, videos:list, errMsg:str):

    ig_model = igService.Find(shortcode)
    # 進來先增次數
    ig_model.retry += 1
    igService.Edit(ig_model)

    if errMsg:
        logging.info(f"====== download {shortcode} was falied, error message : {errMsg} ")
        if ig_model.retry >= _config.max_retry_times:
            ig_model.status = Status.FAILED
            igService.Edit(ig_model)
            return
    else:
        logging.info(f"====== download {shortcode}  was success,  get photos({len(photos)}) amd videos ({len(videos)})")
        ig_model.owner = owner
        ig_model.status = Status.IG_POST_DOWNLOADED
        ig_model.save_path = folder

        if len(photos) >= 1:
            logging.info(f"======download photos list : { ','.join(photos) }")
            fbService.Add(shortcode, FbPostType.PHOTOS, ig_model.message, ','.join(photos))

        for videoPath in videos:
            logging.info(f"======download video file : { videoPath }")
            fbService.Add(shortcode, FbPostType.VIDEO, ig_model.message, videoPath)

        igService.Edit(ig_model)
        logging.info(f"====== update new IG model:  {ig_model.ToString()}" )

if __name__ == '__main__':

    global igService
    global fbService
    global _config
    _config = Config("sexsexder-igdownloader")
    logging.info(f"Load environment variables:\n{_config.ToString()}")


    try :
        igService = IgService(_config.sqlite_path, _config.ig_username, _config.ig_session_file, _config.ig_download_folder, _config.max_retry_times)
        fbService = FbService(_config.sqlite_path, _config.fb_page_id, _config.fb_group_id, _config.fb_access_token , _config.max_retry_times)
        while True:
            try:

                status_filter = [ Status.WAIT]  #-1:失敗放棄, 0:新資料,
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
                logging.info(f" **** sleep {_config.post_delay}s for next post **** ")
                time.sleep(_config.post_delay)
    except Exception as e:
            logging.error(str(e), exc_info=e)
            logging.info(f"have some error, wait 10 seconds ")
"""

if __name__ == '__main__':
    print("hello")
