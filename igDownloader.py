import instaloader 
import os

# Get instance
L = instaloader.Instaloader()

username="jimmy947788"

# Optionally, login or load session
# 不從程式登入因為我的帳號要靠簡訊2階段驗證
# 先用指令來登入保存session之後 程式只要load session 就好
# $> instaloader --login=your_username
#password=""
#L.login(username, password)        # (login)
#L.interactive_login(username)      # (ask password on terminal)

L.load_session_from_file(username) # (load session created w/
                                    #  `instaloader -l USERNAME`)

shortcode = "CNhoYhrhRyL" #https://www.instagram.com/p/COCOx3UnJIG/
post = instaloader.Post.from_shortcode(L.context, shortcode)

print(f"owner_username={post.owner_username}")

save_path = f"{post.owner_username}-{shortcode}"
if not os.path.exists(save_path):
    os.makedirs(save_path)

L.download_post(post, target=save_path)
