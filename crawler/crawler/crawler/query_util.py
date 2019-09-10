from .database import connection
from .err_monitor import error_handle
import traceback
import time





cursor = connection.cursor()


def query_merch_item_info(id,type):
    try:
        sql = "SELECT * FROM merch_item WHERE third_party_product_id='%s' and  third_party_type='%s'" % (id,type)
        cursor.execute(sql)
        return cursor.fetchone()
    except Exception as e:
        traceback.format_exc()
        error_handle(e, traceback.format_exc())
        return


def query_pv_item_info(url):
    try:
        sql = "SELECT * FROM pv WHERE source_url='%s'" % url
        cursor.execute(sql)
        return cursor.fetchone()
    except Exception as e:
        traceback.format_exc()
        error_handle(e, traceback.format_exc())
        return
    

def query_post_info(id):
    try:
        sql = "SELECT * FROM influencer_post_detail WHERE third_party_post_id=%s and third_party_type=2" % id
        print(sql)
        cursor.execute(sql)
        return cursor.fetchone()
    except Exception as e:
        traceback.format_exc()
        error_handle(e, traceback.format_exc())
        return
    

def query_influencer_info(name):
    try:
        name = connection.escape_string(name)
        sql = "SELECT * FROM influencer_platform WHERE third_party_id='%s' and third_party_type=2" % name
        print(sql)
        cursor.execute(sql)
        return cursor.fetchone()
    except Exception as e:
        traceback.format_exc()
        error_handle(e, traceback.format_exc())
        return



