
class FbPost(object):
    def __init__(self):
        self.id = -1
        self.shortcode = None
        self.type = 0                       #1:照片, 2:影片
        self.message = None
        self.files = []
        self.link = None
        self.status = 0                     #-1:失敗放棄, 0:新資料, 1:發送粉專 2:分享社團,
        self.retry = 0
        self.create_time = None
        self.update_time= None

    def create_table_script():
        return """
        CREATE TABLE `fb_post` (
            `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `shortcode`	BLOB NOT NULL,
            `type`	INTEGER NOT NULL DEFAULT 1,
            `message`	TEXT,
            `files`	TEXT,
            `link`	TEXT,
            `status`	INTEGER NOT NULL DEFAULT 0,
            `retry`	INTEGER NOT NULL DEFAULT 0,
            `create_time`	TIMESTAMP NOT NULL,
            `update_time`	TIMESTAMP NOT NULL
        );"""

    def ToString(self):
        return f"""
            id={self.id}, 
            shortcode={self.shortcode}, 
            type={self.type}, 
            message={self.message}, 
            files={self.files}, 
            link={self.link}, 
            status={self.status}, 
            retry={self.retry}, 
            create_time={self.create_time}, 
            update_time={self.update_time}, 
            """