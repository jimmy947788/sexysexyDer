import sys
import traceback
import facebook

if __name__ == '__main__':
    try:
        #FB_PAGE_ID=102168518663747
        _fb_group_id="360767725261103"
        _fb_access_token="EAAMZB2INCZA8cBAAHD9Tw3Yov3mRwWbH7v5hgWROH4yNZAWOGbdEu5pHZAdFH6iJQ3Yz0E599IZCfybwARiZB5XfcJwo4EKukxMZCLxap0l6K26tZAzxkLCWqAGxTOz8Ca0QbKnOMsc6c0TrNjS1jleK6awKayRhmq076xXHhj4kJXQGs1509TYU"
        post_url = "https://www.facebook.com/102168518663747/posts/205185838362014/"
        graph = facebook.GraphAPI(access_token=_fb_access_token)

        message = "#轉發 #自動發文機器人"
        ret = graph.put_object(_fb_group_id,'feed', message=message,link=post_url)
        print(f"share post to group (result {ret})")
        print(graph.get_connections(_fb_group_id, 'feed'))

    except facebook.GraphAPIError as graphAPIError:
        if graphAPIError.message != "Unsupported post request.":
            print(graphAPIError.message)
            print(graphAPIError.message, graphAPIError)
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
        print(errMsg,e)
        raise Exception("share post to group error")
