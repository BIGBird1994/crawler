from scrapy import Spider,Request
from logging import getLogger
from ..err_monitor import error_handle
from ..items import *
from ..id_util import *
from ..database import conn,connection
from time import sleep
from json import loads
from redis import StrictRedis
import urllib.parse
import re
import traceback


# from ..image_util import handle_images
from ..query_util import *





class spider(Spider):
    name = 'sps'
    api = 'https://www.shopstyle.com/api/v2/products?abbreviatedCategoryHistogram=true&cat={}&device=desktop&includeLooks=true&includeProducts=true&includeSavedQueryId=true&limit=40&locales=all&max-price={}&maxNumFilters=1000&min-price={}&numLooks=20&offset={}&pid=shopstyle&prevCat={}&productScore=LessPopularityEPC&t=new&url=%2Fbrowse%2F{}&useElasticsearch=true&view=angular2'
    col = conn['admin']['shop_style_category_info']
    logger = getLogger(__name__)
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.CrawlerPipeline': 302,
        },
        # 'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        # 'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        # 'SCHEDULER_PERSIST': False,
        # 'REDIS_PARAMS': {
        #     'db': 0,
        #     'password': '1x2yxtabc'
        # },
        # 'REDIS_PROT': '6379',
        # 'REDIS_HOST': '35.221.151.226',
        # 'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.SpiderPriorityQueue',
        'HTTPERROR_ALLOWED_CODES ': [301, 302, 403, 404, 418, 911, 500, 502, 503]
    }
    bucket_name = 'item_total_images'
    
    

    def start_requests(self):
          cursor = self.col.find().skip(4)
          for data in cursor:
              try:
                  kw = data['category_link'].split('/')[-1]
                  meta = {'category_name': data['category_name']}
                  for i in range(1,1000):
                      j = i+1
                      yield Request(url=self.api.format(kw, 10 * j, 10 * i, 40, kw, kw),callback=self.parse_product,dont_filter=True)
              except Exception as e:
                    print(e)
                    error_handle(e,traceback.format_exc())
                    continue
                    
                    
    def parse_product(self, response):
        try:
            resp = loads(response.text)
            if resp.get('products') == [] or 'errorMessage' in response.text:
                return
            for data in resp['products']:
                item = ShopstyleItem()
                mi = MerchItemItem()
                item['id'] = data['id']
                item['json_info'] = data
                item['source_url'] = response.url
                yield item
                mi['id'] = generate_merch_item_gid()
                mi['name'] = data['name']
                
                mi['third_party_product_id'] = data['id']
                mi['original_price'] = data['price']
                if 'salePrice' not in data.keys():
                   mi['current_price'] = data['price']
                else:
                    mi['current_price'] = data['salePrice']
                mi['description'] = data['description']
                mi['platform'] = 'ShopStyle'
                mi['third_party_type'] = 2
                mi['source_url'] = data['clickUrl']
                brand = data.get('brand', None)
                if brand:
                    mi['brand'] = brand.get('name')
               
                if data.get('retailer'):
                    mi['retailer'] = data.get('retailer').get('name')

                if data.get('categories'):
                    mi['third_party_category_name'] = data['categories'][0]['fullName']
                    mi['third_party_category_id'] = data['categories'][0]['numId']
                
                print(mi)
                exist = query_merch_item_info(mi['third_party_product_id'])
                if exist:
                    print('====exist stop making pv item')
                    mi['exist'] = 1
                    mi['id'] = exist.get('id')
                    yield mi
                    # return
                else:
                    mi['id'] = generate_merch_item_gid()
                    yield mi
                imgs = [data['image']['sizes']['Best']['url']]
                for _ in data['alternateImages']:
                    imgs.append(_['sizes']['Best']['url'])
                if not imgs:
                    error_handle(err_msg='{} ,has no images'.format(response.url), err_path='')
                    return
                imgs = list(set(imgs))
                for img in imgs:
                   
                        pv = PvItem()
                        pv['pv_id'] = generate_pv_gid()
                        pv['media_type'] = 0
                        pv['url'] = 'item_total_images/shopstyle_product/{}/{}.jpeg'.format(mi['id'],pv['pv_id'])
                        pv['description'] = data.get('description')
                        pv['source'] = 3
                        pv['source_url'] = img
                        pv['merch_item_id'] = mi['id']
                        yield pv
                        handle_images(img=pv['source_url'], mid=mi['id'],
                                      storage_url=pv['url'].replace('item_total_images/', ''), bucket=self.bucket_name)
                
            offset = re.search(r'offset=(\d+)',response.url).group(1)
            next_page = re.sub('offset=\d+','offset={}'.format(int(offset)+40),response.url)
            self.logger.info('<----- fetch next page {}------>'.format(next_page))
            yield Request(url=next_page,callback=self.parse_product)
        except Exception as e:
            print(e)
            error_handle(e, traceback.format_exc())