import facebook

cfg = {
 "page_id" : "102168518663747", # Step 1
 "access_token" : "EAAMZB2INCZA8cBAJaykdsZBmLYEFOiaZAe4zz55obaN0rfh5ZCqQ6bRGnEBE5A5lOLVYfNsh2X4v9ShcV16aFFL9sUZCwh9bbqHtvJ7nB8zLUkUszhI2n2LvUF6fdFkhBLlXwUTulFuZARqdtUvgfkv0OpsMZCEpQiglHQOk6YwZBLcACIlmMCmx5SQnZCkBK7LyppL3rH9mMhf9ARJIqwYyyPbjWlM3upAvFbqFs1tTv3KQZDZD" #step3
}

graph = facebook.GraphAPI(cfg['access_token'])
graph.put_object(cfg['page_id'],"feed",message='歡迎大家追蹤分享~')