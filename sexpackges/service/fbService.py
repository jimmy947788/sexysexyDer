import json
import facebook
import datetime
import logging
import sys
import requests
import urllib
import traceback
from sexpackges.models.fbPost import FbPost
from sexpackges.dbUtility import DbUtility  

class FbService(object):
    def __init__(self, dbpath,  fb_page_id, fb_group_id, fb_access_token):
        self._dbUtility = DbUtility(dbpath)
        self._fb_page_id = fb_page_id
        self._fb_group_id = fb_group_id
        self._fb_access_token = fb_access_token
        
        if not self._dbUtility.TableExists("fb_post"):
            self._dbUtility.Execute(FbPost.create_table_script(), None)

    def Exists(self, shortcode:str, type:int):
        """[summary]

        Args:
            shortcode (str): IG發文帶碼
            type (int): #1:照片, 2:影片

        Returns:
            [type]: [description]
        """
        sql = "SELECT COUNT(*) FROM [fb_post] WHERE shortcode=? and [type]=?"
        paras = (shortcode, type)
        count = self._dbUtility.QueryCount(sql, paras)
        return count >=1

    def Add(self, shortcode:str, type:int, message:str,  files:str = None):
        link = None
        status = 0
        retry = 0
        create_time = datetime.datetime.now()
        update_time = datetime.datetime.now()
        # insert the data into table
        sql = "INSERT INTO [fb_post] (shortcode, [type], [message], files, link, [status], retry, create_time, update_time) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        paras = (shortcode, type, message, files, link, status, retry, create_time, update_time )
        self._dbUtility.Execute(sql, paras)

    def Edit(self, model:FbPost):
        model.update_time = datetime.datetime.now()
        # insert the data into table 
        sql = "UPDATE [fb_post] SET files=?, link=?, [status]=?, retry=?, update_time=? where id=? "
        paras = (','.join(model.files), model.link, model.status, model.retry, model.update_time, model.id )
        self._dbUtility.Execute(sql, paras)

    def Remove(self, shortcode ):
        # insert the data into table
        sql = "DELETE FROM [fb_post]  WHERE shortcode=?"
        paras = (shortcode,)
        self._dbUtility.Execute(sql, paras)


    def Find(self, id:int):
        """[summary]

        Args:
            shortcode (str): IG文章代碼
            type (int): 1:照片, 2:影片

        Returns:
            [type]: [description]
        """
        sql = "SELECT * FROM [fb_post] where id=? "
        paras = (id, )
        row = self._dbUtility.QueryOne(sql,paras)
        model = FbPost()
        if row:
            model.id = int(row[0])
            model.shortcode = row[1]
            model.type = int(row[2])
            model.message =  row[3]
            model.files = str(row[4]).split(",")
            model.link = row[5]
            model.status = int(row[6])     #-1:失敗放棄, 0:新資料, 1:發送粉專 2:分享社團, 
            model.retry = int(row[7])
            model.create_time = row[8]
            model.update_time= row[9]
        return model

    def FindAll(self, status_filter:list=None, retryless=3) :
        """[summary]

        Args:
            status_filter (list, optional):  要查詢狀態，可以送多個。 Defaults to None.
                -1:失敗放棄, 0:新資料, 1:發送粉專 2:分享社團, 
            retry (int, optional): 重試次數 Defaults to 3.

        Returns:
            [type]: [description]
        """
        result = list()
        if status_filter:
            sfilter = ','.join(str(x) for x in status_filter)
            filter = f" and status in ({sfilter}) "
        else:
            filter = ""
        sql = f"SELECT * FROM [fb_post] WHERE retry<{retryless} {filter} "
        rows = self._dbUtility.QueryRows(sql)
        for row in rows:
            model = FbPost()
            model.id = int(row[0])
            model.shortcode = row[1]
            model.type = int(row[2])
            model.message =  row[3]
            model.files = str(row[4]).split(",")
            model.link = row[5]
            model.status = int(row[6])     #-1:失敗放棄, 0:新資料, 1:發送粉專 2:分享社團, 
            model.retry = int(row[7])
            model.create_time = row[8]
            model.update_time= row[9]
            result.append(model)
            
        return result

    def PostPhotos(self, photoFiles:list, ig_owner:str, ig_linker:str, message:str):
        try:
            cfg = {
                "page_id" : self._fb_page_id, 
                "access_token" :  self._fb_access_token
            }
            graph = facebook.GraphAPI(cfg['access_token'])

            photo_id_list = []
            i = 0
            for photo in photoFiles:
                with open(photo, "rb") as photo:
                    photo_id = graph.put_photo(photo, album_id=f'{self._fb_page_id}/photos',published=False)['id']
                    photo_id_list.append(photo_id)
                logging.debug(f"upload photo {photo} and get photo_id: {photo_id}).  {i+1}/{len(photoFiles)}")
                i+=1

            args=dict()
            args["message"]= f"{message}\n#自動發文機器人\n\n\n{ig_owner} 的IG傳送門 {ig_linker}"
            for photo_id in photo_id_list:
                key="attached_media["+str(photo_id_list.index(photo_id))+"]"
                args[key]="{'media_fbid': '"+photo_id+"'}"

            result = graph.request(path=f'/{self._fb_page_id}/feed', args=None, post_args=args, method='POST')
            logging.debug(f"post feed to page (result {result})")

            if "id" in result:
                post_id = result["id"].split("_")[1]
                post_url  = f"https://www.facebook.com/{self._fb_page_id}/posts/{post_id}/"
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

    def PostVideo(self, videoFile:str, ig_owner:str, ig_linker:str, message:str):
        try:
            title = urllib.parse.quote_plus(f"{ig_owner} 的IG影片")
            description = urllib.parse.quote_plus(f"{message}\n#自動發文機器人\n\n\n{ig_owner} 的IG傳送門 {ig_linker}")
            url = f"https://graph-video.facebook.com/{self._fb_page_id}/videos?description={description}&title={title}&access_token={self._fb_access_token}"
            logging.debug(url)

            logging.debug(f"post video_file={videoFile}") 
            files = {'file': open(videoFile, 'rb')}
            response = requests.post(url, files=files)
            logging.debug(f"response: {response.text}")
            result = json.loads(response.text)

            result_url = None
            if "id" in result:
                postId = result["id"] 
                result_url = f"https://www.facebook.com/sexysexyDer/videos/{postId}"
            if "error" in result:
                message = result["error"]["message"]
                raise Exception(message)
            
            return result_url

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

    def ShareToGroup(self, post_url):
        try:
            graph = facebook.GraphAPI(access_token=self._fb_access_token)

            message = "#轉發 #自動發文機器人"
            ret = graph.put_object(self._fb_group_id,'feed', message=message,link=post_url)
            logging.info(f"share post to group (result {ret})")
            print(graph.get_connections(self._fb_group_id, 'feed'))

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