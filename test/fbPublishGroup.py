import sys
import traceback
import facebook

if __name__ == '__main__':
    try:
        #FB_PAGE_ID=102168518663747
        _fb_group_id="360767725261103"
        _fb_access_token="EAAMZB2INCZA8cBAMOnGJaiWRK1fccQGVZCshd2iSrVQJ5vTyzXFzSda8D7dKDUAbYrZB6ZBAUP68xo1gC0JWdOkJZC60twtYAQjav63gF7KBok1rBpUuMZCsLYGQm5mNrZCi0Hv5Kq3Y7Yt0x9HaZCEZC1b0DwHB48XDldyxnwvgm0ErbRmMP2XtLD"
        post_url = "https://www.facebook.com/102168518663747/posts/205185838362014/"
        graph = facebook.GraphAPI(access_token=_fb_access_token)

        
        #message = "#轉發 #自動發文機器人"
        #ret = graph.put_object(_fb_group_id,'feed', message=message,link=post_url)
        #print(f"share post to group (result:{ret})")
        print(graph.get_connections(_fb_group_id, 'feed'))
        

    except facebook.GraphAPIError as graphAPIError:
        print(f"graphAPIError: {graphAPIError.message}")
        if "Unsupported request" not in graphAPIError.message :
            print(graphAPIError.message)
            print(graphAPIError.message, graphAPIError)
            raise Exception(graphAPIError.message)
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg,e)
        raise Exception("share post to group error")
