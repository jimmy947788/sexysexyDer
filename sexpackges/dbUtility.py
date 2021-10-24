import sqlite3
import logging

class DbUtility(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath        

    def QueryOne(self, sql:str, paras:tuple):

        logging.debug(f"query command: {sql}\n\t parameters:{paras}")
        connection = None
        cursor = None
        try:
            connection = sqlite3.connect( self.dbpath,
                detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
            cursor = connection.cursor()
            cursor.execute(sql, paras)
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def QueryRows(self, sql:str, paras:tuple = None):
        logging.debug(f"query command: {sql}\n\t parameters:{paras}")
        connection = None
        cursor = None
        try:
            connection = sqlite3.connect( self.dbpath,
                detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
            cursor = connection.cursor()
            if paras :
                cursor.execute(sql, paras)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def QueryCount(self, sql:str, paras:tuple):
        result = self.QueryOne(sql, paras)
        return int(result[0])

    def TableExists(self, table_name):
        sql = f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name=? ";
        paras = (table_name, )
        return self.QueryCount(sql, paras)  == 1

    def Execute(self, sql:str, paras:tuple):
        logging.debug(f"execute command: {sql}\n\t parameters:{paras}")
        connection = None
        cursor = None
        try:
            # make the database connection with detect_types 
            connection = sqlite3.connect(self.dbpath,
                detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
            cursor = connection.cursor()
            if paras == None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, paras)

            # close the cursor and database connection 
            connection.commit()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


 
