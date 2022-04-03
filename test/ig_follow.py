from turtle import pos
import instaloader 
import os
from instaloader import Profile
# Get instance
L = instaloader.Instaloader()

username="sexsexder"

# Optionally, login or load session
# 不從程式登入因為我的帳號要靠簡訊2階段驗證
# 先用指令來登入保存session之後 程式只要load session 就好
# $> instaloader --login=your_username password=""
#L.login(username, password)        # (login)
#L.interactive_login(username)      # (ask password on terminal)

L.load_session_from_file(username, f"../ig_sessions/session-{username}") # (load session created w/
                                    #  `instaloader -l USERNAME`)
profile = Profile.from_username(L.context, username)

for f in profile.get_followers():
    print(f"https://www.instagram.com/{f.username}/?hl=zh-tw")