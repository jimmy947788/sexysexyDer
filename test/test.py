import requests
from requests.auth import HTTPBasicAuth
import json

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