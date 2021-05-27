import facebook

page_id  =  "102168518663747"  # 粉絲專業

#sexysexydergroup
#access_token = "EAAMZB2INCZA8cBAPYiOI13WJZBiylEDlQZBJy8JJF0ZCLQ8mrxfVizmEFTzneZBdYgZBN9dXvTi2xOeIeNhhdYZAHs5YNSGX58c3K22YQokyTZBLMe93HjRNhMy0o1ZA4GLdppoejssgCPhi1bITY4ANtwZBgCgy1s74zG5d7wapvUABJ1BFZBUdMNr9D4ZBsI4rp7SAJyDH5NT2f524athZByDqMHcUg1vEbLgo9MWLnooQUyFr2kjTTLIwdw"
#用戶權杖
access_token = "EAAMZB2INCZA8cBABoWBZBibdlgekT7aDORktBTBh2oChjym4Ni1TZAvGgymn38UNkFbGGYS5gqZAnGAu4nJoXxxr3lPqkzYe2CsFLFZBW5FjTn0ZB5CxjkAjBlJJcZAgl7uVhgQhVwKArjfQZCnuWkgyfDMxhjd0ZBSogIOGZCHKHRnkhTiLZCYZCpab950ddIQ2aujiuiW9mMVfGM81DZB6sy10e2"

cfg = {
 "page_id" : page_id, # Step 1
 "access_token" : access_token
}

graph = facebook.GraphAPI(cfg['access_token'])
#graph.put_object(cfg['page_id'],"feed",message='歡迎大家追蹤分享~')


img_list = [
    "leeesovely-CPX1nrTNfxn\\2021-05-27_10-07-27_UTC_1.jpg",
    "leeesovely-CPX1nrTNfxn\\2021-05-27_10-07-27_UTC_2.jpg"
]

imgs_id = []
for img in img_list:
    photo = open(img, "rb")
    imgs_id.append(graph.put_photo(photo, album_id='me/photos',published=False)['id'])
    photo.close()

args=dict()
args["message"]="自動發文機器人測試"
for img_id in imgs_id:
    key="attached_media["+str(imgs_id.index(img_id))+"]"
    args[key]="{'media_fbid': '"+img_id+"'}"

graph.request(path='/me/feed', args=None, post_args=args, method='POST')