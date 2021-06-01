from typing import SupportsComplex
import facebook
import instaloader 
import os
import sys
import re
import glob
from pathlib import Path
import shutil
import traceback

id_username="jimmy947788"
ig_session_file="./instaloader-session"

# Optionally, login or load session
# 不從程式登入因為我的帳號要靠簡訊2階段驗證
# 先用指令來登入保存session之後 程式只要load session 就好 
# --login={IG帳號}
# --sessionfie={檔按路徑}
# $> instaloader --login=jimmy947788 --sessionfile=instaloader-session

fb_page_id  =  "102168518663747"  # 妹不就好棒棒 粉絲專業ID
fb_group_id = "360767725261103" # 妹不就好棒棒 社團ID
#妹不就好棒棒 用戶權杖
fb_access_token = "EAAMZB2INCZA8cBABGQVGOIb1JSqcOVae4iay7UBRcjqZCZB4bB0fZCFdL7mFnaQSZAxZBTR3ZB42Sh9y0juCb3heJs7gTj2pmrGfYy0H9It0OVo2vUAcKqBRtMrUnAAU1cAIZCalHGH3KK6NaNIM9QAYGyPe5cluDsNZBdj91P1chLIC9it2Lm8t8t"

def igDownloader(url):
    regex = re.compile(r'^(?:https?:\/\/)?(?:www\.)?(?:instagram\.com.*\/p\/)([\d\w\-_]+)(?:\/)?(\?.*)?$')
    match = regex.search(url)
    shortcode = match.group(1)
    print(f"shortcode : {shortcode}")

    # Get instance
    L = instaloader.Instaloader()
    L.load_session_from_file(id_username, ig_session_file) # (load session created w/
    #L.login(username, password)        # (login)
    #L.interactive_login(username)      # (ask password on terminal)

    post = instaloader.Post.from_shortcode(L.context, shortcode)
    #print(f"owner_username={post.owner_username}")
    save_path = "downloads" #os.path.join("downloads", f"{post.owner_username}-{shortcode}")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    print(f"{post.owner_username}'s post {shortcode} downloading....")
    L.download_post(post, target=save_path)

    shortcode_folder = f"downloads/{post.owner_username}/{shortcode}"
    if not os.path.exists(shortcode_folder):
        os.makedirs(shortcode_folder)

    print("move downlods file  to shortcode folder")
    for file in os.listdir(save_path):
        if ".jpg" in file or ".txt" in file or ".json.xz" in file or ".mp4" in file:
            src = os.path.join(save_path, file)
            dst = os.path.join(shortcode_folder, file)
            shutil.move(src, dst)
    
    return (post, shortcode_folder)

def fpPostToPage(post, folder, ig_linker):
    cfg = {
        "page_id" : fb_page_id, 
        "access_token" : fb_access_token
    }
    graph = facebook.GraphAPI(cfg['access_token'])
    #graph.put_object(cfg['page_id'],"feed",message='歡迎大家追蹤分享~')

    # 上傳圖片
    img_list = glob.glob(f"{folder}/*.jpg")
    imgs_id = []
    for img in img_list:
        photo = open(img, "rb")
        imgs_id.append(graph.put_photo(photo, album_id='me/photos',published=False)['id'])
        photo.close()

    args=dict()
    args["message"]= f"防疫期間大家在家裡看妹就好\n我們有最強大的\"工人智慧\"每天篩選發文\n如果覺得不錯再幫忙推薦給朋友壯大社群\n#自動發文機器人\n\n\n{post.owner_username} IG傳送門 {ig_linker}"
    for img_id in imgs_id:
        key="attached_media["+str(imgs_id.index(img_id))+"]"
        args[key]="{'media_fbid': '"+img_id+"'}"

    ret = graph.request(path=f'/{fb_page_id}/feed', args=None, post_args=args, method='POST')
    print(f"post result : {ret}")

    ids = ret["id"].split("_")
    post_url  = f"https://www.facebook.com/{ids[0]}/posts/{ids[1]}/"

    return post_url

def fpPostToGroup(post_url):
    try:
        graph = facebook.GraphAPI(access_token=fb_access_token)

        message = "妹不就好棒棒粉絲專業轉發\n#自動發文機器人"
        graph.put_object(fb_group_id,'feed', message=message,link=post_url)
    except  facebook.GraphAPIError as graphAPIError:
        print(graphAPIError)
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)

if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] :
            ig_linker = sys.argv[1]
            (post, shortcode_folder) = igDownloader(ig_linker)
            post_url = fpPostToPage(post, shortcode_folder, ig_linker)
            fpPostToGroup(post_url)
    else:
        print("please provide IG link")