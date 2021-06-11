import requests
import urllib

pageId = '102168518663747'    # user id (ex. 1603333222111000)
token = "EAAMZB2INCZA8cBABGQVGOIb1JSqcOVae4iay7UBRcjqZCZB4bB0fZCFdL7mFnaQSZAxZBTR3ZB42Sh9y0juCb3heJs7gTj2pmrGfYy0H9It0OVo2vUAcKqBRtMrUnAAU1cAIZCalHGH3KK6NaNIM9QAYGyPe5cluDsNZBdj91P1chLIC9it2Lm8t8t"

"""
url = 'https://graph-video.facebook.com/{user_id}/videos?access_token={token}'.format(
    user_id=_user_id,
    token= _token
)

files = {
    'file': open('198115764_999879234166830_7309441645382858953_n.mp4', 'rb')
}

response = requests.post(url, files=files).text
print(response)
891610248363431
"""

#postId = "891610248363431"
url = f"https://graph-video.facebook.com/{pageId}/videos?description=影片說明&title=影片title&access_token={token}"

video_path = '../worker/src/downloads/tw901173/CP8lbmvHzPO/2021-06-10_16-38-08_UTC.mp4'
files = {'file': open(video_path, 'rb')}
response = requests.post(url, files=files)
postId = response.text
print(f"https://www.facebook.com/sexysexyDer/videos/{postId}")

#2675481499416528
#https://www.facebook.com/sexysexyDer/videos/641102857288055
