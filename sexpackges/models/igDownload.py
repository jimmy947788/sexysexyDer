
class IgDownload(object):
    def __init__(self):
        self.shortcode = None
        self.link = None
        self.message = None
        self.owner = None
        self.status = 0                #-1:失敗放棄, 0:新資料, 1.下載完成
        self.save_path = None
        self.retry = 0
        self.create_time = None
        self.update_time= None

    def create_table_script():
        return """
           CREATE TABLE `ig_download` (
            `shortcode`	TEXT NOT NULL,
            `link`	TEXT,
            `message`	TEXT,
            `owner`	TEXT,
            `status`	INTEGER NOT NULL DEFAULT 0,
            `save_path`	TEXT,
            `retry`	INTEGER NOT NULL DEFAULT 0,
            `create_time`	TIMESTAMP NOT NULL,
            `update_time`	TIMESTAMP NOT NULL,
            PRIMARY KEY(`shortcode`)
        );"""
    
    def ToString(self):
        return f"""
        shortcode={self.shortcode}, 
        link={self.link}, 
        message={self.message}, 
        owner={self.owner}, 
        status={self.status}, 
        save_path={self.save_path}, 
        retry={self.retry}, 
        create_time={self.create_time}, 
        update_time={self.update_time}, 
        """