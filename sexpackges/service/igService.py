
import datetime
import instaloader 
import shutil
import traceback
import os
import sys
import glob
import logging
from sexpackges.models.enum import Status, FbPostType
from sexpackges.models.igDownload import IgDownload
from sexpackges.dbUtility import DbUtility  

class IgService(object):
    def __init__(self, dbpath, ig_username, ig_session_file, ig_download_folder, max_retry_times:int):
        self._dbUtility = DbUtility(dbpath)
        if not self._dbUtility.TableExists("ig_download"):
            self._dbUtility.Execute(IgDownload.create_table_script(), None)

        self._max_retry_times = max_retry_times
        self._ig_download_folder = ig_download_folder
        # Get instance
        self._ig_loader = instaloader.Instaloader()
        self._ig_loader.load_session_from_file(ig_username, ig_session_file) 
        logging.info(f"create ig_loader from IG session file.")


    def Exists(self, shortcode):
        sql = "SELECT COUNT(*) FROM [ig_download] WHERE shortcode=?"
        paras = (shortcode, )
        count = self._dbUtility.QueryCount(sql, paras)
        return count >=1

    def Add(self, shortcode:str, link:str, message:str):
        owner = None
        status = Status.WAIT
        save_path = None
        retry = 0
        create_time = datetime.datetime.now()
        update_time = datetime.datetime.now()
        # insert the data into table
        sql = "INSERT INTO [ig_download] (shortcode, link, [owner], message, [status], save_path, retry, create_time, update_time) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        paras = (shortcode, link, owner, message, status.value, save_path, retry, create_time, update_time )
        self._dbUtility.Execute(sql, paras)

    def Remove(self, shortcode ):
        # insert the data into table
        sql = "DELETE FROM [ig_download]  WHERE shortcode=?"
        paras = (shortcode,)
        self._dbUtility.Execute(sql, paras)

    def Edit(self, model:IgDownload):
        model.update_time = datetime.datetime.now()
        sql = "UPDATE [ig_download] SET [owner]=?, [status]=?, save_path=?, retry=?, update_time=? where shortcode=? "
        paras = (model.owner, model.status.value, model.save_path, model.retry, model.update_time, model.shortcode )
        self._dbUtility.Execute(sql, paras)

    def Find(self, shortcode:str):
        sql = "SELECT * FROM [ig_download] WHERE shortcode=?"
        logging.debug(f"[Find] query command {sql}")

        paras = (shortcode,  )
        row = self._dbUtility.QueryOne(sql,paras)
        model = IgDownload()
        if row:
            model.shortcode = row[0]
            model.link =  row[1]
            model.message = row[2]
            model.owner = row[3]
            model.status = Status(int(row[4]))  #-1:????????????, 0:?????????, 1.????????????
            model.save_path = row[5]
            model.retry = int(row[6])
            model.create_time = datetime.datetime.strftime(row[7],'%Y-%m-%d %H:%M:%S')  
            model.update_time= datetime.datetime.strftime(row[8],'%Y-%m-%d %H:%M:%S')  
        return model

    def FindAll(self, status_filter:list=None) :
        """[summary]
        ??????ig_download ??????
        
        Args:
            status_filter (list, optional):  download????????????????????? Defaults to None.
             -1:????????????, 0:?????????, 1.???????????????None???????????????. 
            retry (int, optional): ??????????????????n Defaults to 3.

        Returns:
            [type]: [description]
        """
        result = list()
        if status_filter:
            sfilter = ','.join(str(x.value) for x in status_filter)
            filter = f" and status in ({sfilter}) "
        else:
            filter = ""
        sql = f"SELECT * FROM [ig_download] WHERE retry<{self._max_retry_times } {filter} ORDER BY create_time ASC"
        logging.debug(f"[FindAll] query command {sql}")

        rows = self._dbUtility.QueryRows(sql, None)
        for row in rows:
            model = IgDownload()
            model.shortcode = row[0]
            model.link =  row[1]
            model.message = row[2]
            model.owner = row[3]
            model.status = Status(int(row[4]))   #-1:????????????, 0:?????????, 1.????????????
            model.save_path = row[5]
            model.retry = int(row[6])
            model.create_time = datetime.datetime.strftime(row[7],'%Y-%m-%d %H:%M:%S')  
            model.update_time= datetime.datetime.strftime(row[8],'%Y-%m-%d %H:%M:%S')  
            result.append(model)
        return result
        
    def Download(self, shortcode):
        shortcode_folder = None
        owner = None
        photo_list = []
        video_list = []
        errMsg = None
        try:
            post = instaloader.Post.from_shortcode(self._ig_loader.context, shortcode)

            logging.debug(f"post {shortcode} downlaoding...")
            self._ig_loader.download_post(post, target= self._ig_download_folder.split("/")[-1])

            owner = post.owner_username
            shortcode_folder = os.path.join( self._ig_download_folder, owner, shortcode)
            logging.info(f"check shortcode folder is {shortcode_folder}")

            if not os.path.exists(shortcode_folder):
                logging.info(f"{shortcode_folder} folder not exists,  create shortcode folder")
                os.makedirs(shortcode_folder)

            # ??????????????????????????? {IG??????}/{shortcode}
            logging.debug(f"move file to shortcode folder.")
            for file in os.listdir( self._ig_download_folder):
                if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
                    src = os.path.join( self._ig_download_folder, file)
                    dst = os.path.join(shortcode_folder, file)
                    shutil.move(src, dst)
            
            # ??????????????????
            logging.debug(f"remove video cover from shortcode folder.")
            video_file_list = glob.glob(f"{shortcode_folder}/*.mp4")
            for video_file in video_file_list:
                image_file = video_file.replace(".mp4", ".jpg")
                os.remove(image_file)

            # ????????????????????????
            photo_list =  glob.glob(f"{shortcode_folder}/*.jpg")

            # ????????????????????????
            video_list = glob.glob(f"{shortcode_folder}/*.mp4")

            return (shortcode, owner, shortcode_folder, photo_list, video_list, errMsg)
            
        except Exception as e:
            error_class = e.__class__.__name__ #??????????????????
            detail = e.args[0] #??????????????????
            cl, exc, tb = sys.exc_info() #??????Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #??????Call Stack?????????????????????
            fileName = lastCallStack[0] #???????????????????????????
            lineNum = lastCallStack[1] #?????????????????????
            funcName = lastCallStack[2] #???????????????????????????
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            logging.error(errMsg,e)
            #raise Exception("Download IG post has error")
            isSuccess = False
            return (shortcode, owner, shortcode_folder, photo_list, video_list, errMsg)

        