import logging
import datetime
import sys,os
import pymysql

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname('__file__')))))


from .database import connection



cursor = connection.cursor()


def error_handle(err_msg,err_path):
    if not err_path or not err_msg:
        return
    try:
        sql = '''INSERT INTO spider_err_msg (err_msg,err_path) VALUES (%s,%s)'''
        cursor.execute(sql, (str(err_msg),str(err_path)))
        return connection.commit()
    except Exception as e:
        logging.error(e)
        
