import instaloader 
import os
from instaloader import BadResponseException, PrivateProfileNotFollowedException, Profile
# Get instance
L = instaloader.Instaloader()

username="sexsexder"

# Optionally, login or load session
# 不從程式登入因為我的帳號要靠簡訊2階段驗證
# 先用指令來登入保存session之後 程式只要load session 就好
# $> instaloader --login=your_username
#password=""
#L.login(username, password)        # (login)
#L.interactive_login(username)      # (ask password on terminal)

L.load_session_from_file(username, f"../ig_sessions/session-{username}") # (load session created w/
                                    #  `instaloader -l USERNAME`)

"""
profile = Profile.from_username(L.context, username)

for f in profile.get_followers():
    print(f"https://www.instagram.com/{f.username}/?hl=zh-tw")

"""
try:
    shortcode = "COCOx3UnJIG" #https://www.instagram.com/p/COCOx3UnJIG/
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    print(f"owner_username={post.owner_username}")

    #owner_profile = Profile.from_username(L.context, post.owner_username)
    #print(owner_profile.is_private)

    L.download_post(post, target=post.owner_username)
except BadResponseException as e:
    print(e)
# except PrivateProfileNotFollowedException as e:
#   print(e.message)