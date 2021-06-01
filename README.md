"# sexysexyDer" 


## 初始化專案

### 安裝套件
```bash
pip3 install -r requirements.txt
```


docker build -t sexysexyder .
docker run  -d -p 5000:5000  --name sexysexyder-bot  sexysexyder

docker run -it -p 5000:5000 -v /home/pi/sexysexyDer:/usr/src/app --name sexysexyder-bot sexysexyder /bin/bash

docker container rm sexysexyder-bot 
### 存取權杖
https://developers.facebook.com/tools/explorer/913524566157255/


# Optionally, login or load session
# 不從程式登入因為我的帳號要靠簡訊2階段驗證
# 先用指令來登入保存session之後 程式只要load session 就好 
# --login={IG帳號}
# --sessionfie={檔按路徑}
# $> instaloader --login=jimmy947788 --sessionfile=instaloader-session