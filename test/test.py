import requests
from requests.auth import HTTPBasicAuth
import json
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

"""
response = requests.get('http://www.daedalus.com.tw:8001/api/queues/', auth = HTTPBasicAuth('sexsexder', '1qaz@WSX'))

# print request object
jsonObj = json.loads(response.text)
print(jsonObj[0]["messages"])
"""

ddd="/usr/app/downloads"
print(ddd.split("/")[-1])

ccc="downloads"
print(ccc.split("/")[-1])


url = "https://www.instagram.com/reel/CR_QcmBBlQ2/?utm_source=ig_web_copy_link"
u = urlparse(url)
print(u)
print(f"path : {u.path}")
print(u.path.split('/')[-2:-1][0])
