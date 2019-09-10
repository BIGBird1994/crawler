# -*- coding: utf-8 -*-

import os
import traceback

from .database import connection, conn
# from scrapy.pipelines.files import FilesPipeline
# from scrapy.pipelines.images import ImagesPipeline
# from scrapy.pipelines.files import GCSFilesStore
from .err_monitor import error_handle
from .items import *

path = "{}/InfluenceForce-1400842c21fd.json".format(os.path.split(os.path.realpath(__file__))[0])
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path


class CrawlerPipeline(object):
    
    def __init__(self):
        self.cursor = connection.cursor()
        self.col = conn['admin']['shop_style_product_info']
    
    def process_item(self, item, spider):
        for k in item.copy():
            if not item[k] and item[k] != 0:
                del item[k]
            elif isinstance(item[k], str):
                item[k] = connection.escape_string(item[k])
        
        try:
            if isinstance(item, InfluencerPlatformItem):
                if item.get('update'):
                    print('==== update table {}'.format(item))
                    item.pop('update')
                    influencer_id = item.pop('influencer_id')
                    third_party_type = item.pop('third_party_type')
                    keys = item.keys()
                    values = tuple(item.values())
                    fields = ['%s=' % i + '"%s"' for i in keys]
                    sql = 'UPDATE influencer_platform SET %s WHERE influencer_id="%s" and third_party_type="%s"' % (','.join(fields), influencer_id, third_party_type)
                
                else:
                    keys = item.keys()
                    values = tuple(item.values())
                    fields = ','.join(keys)
                    temp = ','.join(['"%s"'] * len(keys))
                    sql = 'INSERT INTO influencer_platform (%s) VALUES (%s)' % (fields, temp)
            
            
            
            elif isinstance(item, InfluencerPostDetailItem):
                if item.get('update'):
                    print('==== update table {}'.format(item))
                    item.pop('update')
                    influencer_post_id = item.pop('id')
                    third_party_type = item.pop('third_party_type')
                    keys = item.keys()
                    values = tuple(item.values())
                    fields = ['%s=' % i + '"%s"' for i in keys]
                    sql = 'UPDATE influencer_post_detail SET %s WHERE id="%s" and third_party_type="%s"' % (','.join(fields), influencer_post_id, third_party_type)
                else:
                    keys = item.keys()
                    values = tuple(item.values())
                    fields = ','.join(keys)
                    temp = ','.join(['"%s"'] * len(keys))
                    sql = 'INSERT INTO influencer_post_detail (%s) VALUES (%s)' % (fields, temp)
            
            
            
            elif isinstance(item, MerchItemItem):
                if item.get('exist') == 1:
                    print('==== update mech_item {}'.format(item))
                    item.pop('exist')
                    third_party_type = item.pop('third_party_type')
                    third_party_product_id = item.pop('third_party_product_id')
                    keys = item.keys()
                    values = tuple(item.values())
                    fields = ['%s=' % i + '"%s"' for i in keys]
                    sql = 'UPDATE merch_item SET %s WHERE third_party_product_id="%s" and third_party_type="%s" ' % (','.join(fields), third_party_product_id, third_party_type)
                
                
                else:
                    print('===== insert merch_item {} ===='.format(item))
                    keys = item.keys()
                    values = tuple(item.values())
                    fields = ','.join(keys)
                    temp = ','.join(["'%s'"] * len(keys))
                    sql = 'INSERT INTO merch_item (%s) VALUES (%s)' % (fields, temp)
            
            
            
            elif isinstance(item, PvItem):
                keys = item.keys()
                values = tuple(item.values())
                fields = ','.join(keys)
                temp = ','.join(['"%s"'] * len(keys))
                sql = 'INSERT INTO pv (%s) VALUES (%s)' % (fields, temp)
            
            
            elif isinstance(item, ReviewItem):
                if 'review_id' not in item.keys():
                    del item
                keys = item.keys()
                values = tuple(item.values())
                fields = ','.join(keys)
                temp = ','.join(['"%s"'] * len(keys))
                sql = 'INSERT INTO product_reviews (%s) VALUES (%s)' % (fields, temp)
            
            elif isinstance(item, PostMerchItemMapItem):
                keys = item.keys()
                values = tuple(item.values())
                fields = ','.join(keys)
                temp = ','.join(['"%s"'] * len(keys))
                sql = 'INSERT INTO post_merch_item_map (%s) VALUES (%s)' % (fields, temp)
            
            
            
            elif isinstance(item, ShopstyleItem):
                self.col.update(
                    { 'id': item['id'] }, dict(item), True
                )
            
            print(sql % values)
            with connection.cursor() as cur:
                cur.execute(sql % values)
                return connection.commit()
        
        except Exception as e:
            traceback.format_exc()
            error_handle(e, traceback.format_exc())
        
        

# class GCSFilesStoreJSON(GCSFilesStore):
#
#     CREDENTIALS = {
#         "type": "service_account",
#         "project_id": "influneceforce",
#         "private_key_id": "1400842c21fd82889786b8d9377a725a21a20b77",
#         "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCOX4vPHYdsBDTt\nQ0PO9YK8W/ojrOhZ6heHlK9fLH6X7tMMb/dLOQFkVaaQFStiBUiKN2Lix1IW4/A4\nD7Klx5NDQzR0fK+Jx2xxe7A208+8h/ufo76pq0hk6CfmLHkDPAfQhw/j718UaPk6
#         \nZP2Ml6r1vapqAIwQGV7akqIHilvfAki72O5IhcCpOqoI58NKROZP6ocx1vp5Sq+V\nstPlru87HsWkBhmY6K0nJsSiMS0nxj8VKjesXl1X8TD6y7hpimbjaQ6Q+ETf4Zxw\nYF33W5rQQACES+/u+U/wOsMAvOu1/0lkDAEF7ifgQL3dR7IdWRX81eLNzOAA2XTe\nCY1qwK0VAgMBAAECggEACs/kvTDf5OsY3d/a2W+5ovZVM7pg1ts5ODmpa8/kOUOQ
#         \n0YP7QsIsgeMjSBPjfIksLhrwroo2iLh8uLUweviCDXygEiyZ5Bu595BOHIvPXeDx\n0fjMdPQmBku/I/LCqeU4LrTjFwtJrDIgozeiLbgi6pChzXUHLf3PP0gdd/cg7PmR\nbJZ9ymCicSyFIzT3IxbpOMcXO1Q75bsyrsHdc23XD7eFoDdMysPTtlECuipj19fP\nYklsXYE3dEjbg0UmIXQ54GupY8HkeCMceQ3aJRzhyuGeaxjJhx8jXy1J7SUdTYz0
#         \ndjePNK2MzmYdHuwAwCB2dvByoxBaGj6S0nBR74UDIQKBgQDEHJQiCYfkDAdPiAIz\nQX24kY/n4Ggf3XWQYzT5GF5DLBim40uKZ1gAccL+/Nci5d/lRvcR2xfv8x2NbIuy\nSGzsRStI7nZ2dlMJ1uu58lJzxhYCahhIXv+7/T5xvFQ3EJbSEJ7gVC+0ChWJtSLk\nh1JP5NtFWn4i4+CcjSxF6GwNOQKBgQC52dwAgyy61H803a7eKeaXJzeX8On7RdNa
#         \nCwL2QQhTtqA04lIXV81YZYXfTb/H/r3OnO717wbnvFsU94G9Q5xbKDfQrA9L97Km\nV7Py7Nvx0KMB7Fx2jEnlguw2ZR7e/uT+VpAVNjSuKxg/kut31aR/3K1T3qgGLIXH\nIqq/09w6vQKBgQCF2WOZX5vqH/OVaqTlyts978uiXV1z8jjdVXjAUstzWVNyBEx4\nqFQ96WdHldZYMUEBQdA71aee0/XloqIuCpSdJhCG9IrSC6xdWN0GysdP0XEQMM1m\nB8DP0+acxgdMlfv6X
#         /Gv9oWgggl1NbYc9+dMNE0cJslUkueosgn3pMyqsQKBgF1y\n3v1e98nFeWTipr/Mv8Z3EKwUlgIjfP9ElCuwTXiSVoHg3rggDP+KpMLAfFMakuPl\n4v3EP2ucOQwU26aH7YGkelQxf8uJ88lSRgg68ujnKF+aMm/lYG7H4vAC7n/gGNKO\nQgp4ZArDXoDw5fcudHVaR8jpJwFbt7SGiObFp3HdAoGBAKj9r1EVzLD9PnG7UHrS\nhgBbvkGDXktyda56PyPvxfQsDBv0oCSG8P
#         +5LMdZlKGPkUEOzOugfOtzITtk9Ewy\nxgWbiCqnM5O1fPL5G369whG/+p3PA5wbWfjLTry31a/ilpoA7lLYIxQuj+BNpJQJ\nRlLXJbXK5TOiGQm35lXjbcP+\n-----END PRIVATE KEY-----\n",
#         "client_email": "605676065177-compute@developer.gserviceaccount.com",
#         "client_id": "116372402084222238038",
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#         "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/605676065177-compute%40developer.gserviceaccount.com"
#     }
#
#     def __init__(self, uri):
#         from google.cloud import storage
#         client = storage.Client.from_service_account_info(self.CREDENTIALS)
#         bucket, prefix = uri[5:].split('/', 1)
#         self.bucket = client.bucket(bucket)
#         self.prefix = prefix

# class GCSFilePipeline(FilesPipeline):
#     def __init__(self, store_uri, download_func=None, settings=None):
#         super(GCSFilePipeline, self).__init__(store_uri, download_func, settings)
#
# class MyPipeline(ImagesPipeline):
#     logger = logging.getLogger(__name__)
#
#     def get_media_requests(self, item, info):
#         try:
#             if isinstance(item, PvItem):
#                 yield scrapy.Request(url=item['source_url'], meta={'item': item})
#             else:
#                 pass
#         except Exception as e:
#             print(e)
#             error_handle(e, traceback.format_exc())
#
#     def file_path(self, request, response=None, info=None):
#         item = request.meta['item']
#         path = item['url'].replace('amazon_image/', '')
#         return path
#
#     def item_completed(self, results, item, info):
#         try:
#             if isinstance(item, PvItem) or self.images_result_field in item.fields:
#                 item[self.images_result_field] = [x for ok, x in results if ok]
#             return item
#         except Exception as e:
#             print(e)
#             error_handle(e, traceback.format_exc())
