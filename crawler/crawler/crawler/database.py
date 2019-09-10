import pymysql,pymongo
import sys,os

import urllib.parse


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
print(sys.path)

MYSQL_DB = 'thresh'
MYSQL_USER = 'tao'
MYSQL_PASS = 'tao!23'
MYSQL_HOST = '35.233.214.39'
# mysql
connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                             password=MYSQL_PASS, db=MYSQL_DB,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor,
                             )

# mongo
username = urllib.parse.quote_plus('root')
password = urllib.parse.quote_plus('1x2yxtabc1995')
conn = pymongo.MongoClient(host='mongodb://%s:%s@35.221.151.226' % (username, password), port=27017)



    

