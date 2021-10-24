
import datetime
import instaloader 
import shutil
import traceback
import os
import sys
import glob
import logging
from sexpackges.models.igDownload import IgDownload
from sexpackges.dbUtility import DbUtility  

class IgService(object):
    def __init__(self, dbpath, ig_username, ig_session_file, ig_download_folder):
        self._dbUtility = DbUtility(dbpath)
        if not self._dbUtility.TableExists("ig_download"):
            self._dbUtility.Execute(IgDownload.create_table_script(), None)

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
        status = 0
        save_path = None
        retry = 0
        create_time = datetime.datetime.now()
        update_time = datetime.datetime.now()
        # insert the data into table
        sql = "INSERT INTO [ig_download] (shortcode, link, [owner], message, [status], save_path, retry, create_time, update_time) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        paras = (shortcode, link, owner, message, status, save_path, retry, create_time, update_time )
        self._dbUtility.Execute(sql, paras)

    def Remove(self, shortcode ):
        # insert the data into table
        sql = "DELETE FROM [ig_download]  WHERE shortcode=?"
        paras = (shortcode,)
        self._dbUtility.Execute(sql, paras)

    def Edit(self, model:IgDownload):
        model.update_time = datetime.datetime.now()
        # insert the data into table update_sql = "UPDATE [ig_post]  SET status = ?, post_time=?  WHERE shortcode=?"
        sql = "UPDATE [ig_download] SET [owner]=?, [status]=?, save_path=?, retry=?, update_time=? where shortcode=? "
        paras = (model.owner, model.status, model.save_path, model.retry, model.update_time, model.shortcode )
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
            model.status = int(row[4])  #-1:失敗放棄, 0:新資料, 1.下載完成
            model.save_path = row[5]
            model.retry = int(row[6])
            model.create_time = datetime.datetime.strftime(row[7],'%Y-%m-%d %H:%M:%S')  
            model.update_time= datetime.datetime.strftime(row[8],'%Y-%m-%d %H:%M:%S')  
        return model

    def FindAll(self, status_filter:list=None, retryless=3) :
        """[summary]
        查詢ig_download 資料
        
        Args:
            status_filter (list, optional):  download狀態可以送多格 Defaults to None.
             -1:失敗放棄, 0:新資料, 1.下載完成，None全部查出來. 
            retry (int, optional): 重試次數小於n Defaults to 3.

        Returns:
            [type]: [description]
        """
        result = list()
        if status_filter:
            sfilter = ','.join(str(x) for x in status_filter)
            filter = f" and status in ({sfilter}) "
        else:
            filter = ""
        sql = f"SELECT * FROM [ig_download] WHERE retry<{retryless} {filter} ORDER BY create_time ASC"
        logging.debug(f"[FindAll] query command {sql}")

        rows = self._dbUtility.QueryRows(sql, None)
        for row in rows:
            model = IgDownload()
            model.shortcode = row[0]
            model.link =  row[1]
            model.message = row[2]
            model.owner = row[3]
            model.status = int(row[4])  #-1:失敗放棄, 0:新資料, 1.下載完成
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

            # 搬移下載檔案到路徑 {IG帳號}/{shortcode}
            logging.debug(f"move file to shortcode folder.")
            for file in os.listdir( self._ig_download_folder):
                if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
                    src = os.path.join( self._ig_download_folder, file)
                    dst = os.path.join(shortcode_folder, file)
                    shutil.move(src, dst)
            
            # 刪除影片封面
            logging.debug(f"remove video cover from shortcode folder.")
            video_file_list = glob.glob(f"{shortcode_folder}/*.mp4")
            for video_file in video_file_list:
                image_file = video_file.replace(".mp4", ".jpg")
                os.remove(image_file)

            # 取的下載照片清單
            photo_list =  glob.glob(f"{shortcode_folder}/*.jpg")

            # 取的下載影片清單
            video_list = glob.glob(f"{shortcode_folder}/*.mp4")

            return (shortcode, owner, shortcode_folder, photo_list, video_list, errMsg)
            
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
            #raise Exception("Download IG post has error")
            isSuccess = False
            return (shortcode, owner, shortcode_folder, photo_list, video_list, errMsg)

        