import facebook
import instaloader 
import os
import sys
import re
import glob

id_username="jimmy947788"
ig_session_file ="C:\\Users\\Jimmy Wu\\AppData\\Local\\Instaloader\\session-jimmy947788" 
# Optionally, login or load session
# 不從程式登入因為我的帳號要靠簡訊2階段驗證
# 先用指令來登入保存session之後 程式只要load session 就好
# $> instaloader --login=your_username
#password=""
#L.login(username, password)        # (login)
#L.interactive_login(username)      # (ask password on terminal)


fb_page_id  =  "102168518663747"  # 妹不就好棒棒 粉絲專業
#妹不就好棒棒 用戶權杖
fb_access_token = "EAAMZB2INCZA8cBABoWBZBibdlgekT7aDORktBTBh2oChjym4Ni1TZAvGgymn38UNkFbGGYS5gqZAnGAu4nJoXxxr3lPqkzYe2CsFLFZBW5FjTn0ZB5CxjkAjBlJJcZAgl7uVhgQhVwKArjfQZCnuWkgyfDMxhjd0ZBSogIOGZCHKHRnkhTiLZCYZCpab950ddIQ2aujiuiW9mMVfGM81DZB6sy10e2"

if len(sys.argv) == 2:
    if sys.argv[1] :
        raw_url = sys.argv[1]
        regex = re.compile(r'^(?:https?:\/\/)?(?:www\.)?(?:instagram\.com.*\/p\/)([\d\w\-_]+)(?:\/)?(\?.*)?$')
        match = regex.search(raw_url)
        shortcode = match.group(1)
        print(f"shortcode : {shortcode}")

        # Get instance
        L = instaloader.Instaloader()
        L.load_session_from_file(id_username, ig_session_file) # (load session created w/
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"owner_username={post.owner_username}")
        save_path = f"{post.owner_username}-{shortcode}"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        L.download_post(post, target=save_path)

        ##############################################################################
        cfg = {
            "page_id" : fb_page_id, 
            "access_token" : fb_access_token
        }
        graph = facebook.GraphAPI(cfg['access_token'])
        #graph.put_object(cfg['page_id'],"feed",message='歡迎大家追蹤分享~')
        
        img_list = glob.glob(f"{save_path}/*.jpg")

        imgs_id = []
        for img in img_list:
            photo = open(img, "rb")
            imgs_id.append(graph.put_photo(photo, album_id='me/photos',published=False)['id'])
            photo.close()

        args=dict()
        args["message"]= f"防疫期間大家在家裡看妹就好，我們有最強大的\"工人智慧\"每天篩選發文。\n如果覺得不錯再幫忙推薦給朋友壯大社群\n#自動發文機器人測試\n\n\nIG 傳送門 {raw_url}"
        for img_id in imgs_id:
            key="attached_media["+str(imgs_id.index(img_id))+"]"
            args[key]="{'media_fbid': '"+img_id+"'}"

        graph.request(path='/me/feed', args=None, post_args=args, method='POST')

else:
    print("please provide IG link")
"""
L.load_session_from_file(id_username, ig_session_file) # (load session created w/

shortcode = "CPX1nrTNfxn" #https://www.instagram.com/p/COCOx3UnJIG/
post = instaloader.Post.from_shortcode(L.context, shortcode)

print(f"owner_username={post.owner_username}")

save_path = f"{post.owner_username}-{shortcode}"
if not os.path.exists(save_path):
    os.makedirs(save_path)

L.download_post(post, target=save_path)
"""