# -*- coding: utf-8 -*-
from scrapy import Request,Spider
from ..err_monitor import error_handle
from ..items import MerchItemItem,PvItem
from ..id_util import *
import logging
import re
import traceback
import os
import datetime
import logging
from json import loads
from ..image_util import handle_images
from ..query_util import query_merch_item_info





class spider(Spider):
      name = 'nps'
      start_urls = [
          'https://www.neimanmarcus.com/c/womens-clothing-cat000001?navpath=cat000000_cat000001',
          'https://www.neimanmarcus.com/c/shoes-cat000141?navpath=cat000000_cat000141',
          'https://www.neimanmarcus.com/c/handbags-cat13030735?navpath=cat000000_cat13030735',
          'https://www.neimanmarcus.com/c/jewelry-accessories-cat4870731?navpath=cat000000_cat4870731',
      ]
      url = 'https://www.neimanmarcus.com{}'
      custom_settings = {
          'DOWNLOAD_TIMEOUT': 20,
          'ITEM_PIPELINES' : {
          'crawler.pipelines.CrawlerPipeline': 302,
      },
          'SCHEDULER' :"scrapy_redis.scheduler.Scheduler",
          'DUPEFILTER_CLASS' : "scrapy_redis.dupefilter.RFPDupeFilter",
          'SCHEDULER_PERSIST' : True ,
          'REDIS_PARAMS' : {
              'db': 1,
              'password': '1x2yxtabc'
          },
          'REDIS_PROT' : '6379',
          'REDIS_HOST' : '35.221.151.226',
          'SCHEDULER_QUEUE_CLASS' : 'scrapy_redis.queue.SpiderPriorityQueue',
          'HTTPERROR_ALLOWED_CODES ': [301, 302, 403, 404, 418, 911, 500, 502, 503]
      }
      bucket_name = 'item_total_images'
      
      
      
      def parse(self, response):
          
          try:
              for data in response.xpath('//ul[@class="left-nav__category"]/li/a'):
                  href = data.xpath('./@href').extract_first(default=None)
                  yield Request(url=self.url.format(href),callback=self.parse_page)
          except Exception as e:
            traceback.print_exc()
            error_handle(response.url, traceback.print_exc())
            
            

      def parse_page(self, response):
          
          try:
              for data in response.xpath('//a[@class="product-thumbnail__link"]'):
                  href = data.xpath('./@href').extract_first(default=None)
                  yield Request(url=self.url.format(href),callback=self.parse_detail)
            
              next_page = response.xpath('//a[@aria-label="Next"]/@href').extract_first(default=None)
              if next_page:
                  logging.info('==== fetch next page {}'.format(next_page))
                  yield Request(url=self.url.format(next_page),callback=self.parse_page)
          except Exception as e:
              traceback.print_exc()
              error_handle(response.url,traceback.print_exc())
          
          
      
      def parse_detail(self, response):
          
          try:
              mi = MerchItemItem()
              data = response.xpath('//div[@class="product-page__linked-data"]/script/text()').extract_first(default=None)
              if not data:
                  logging.warning('==== data {}'.format(data))
                  return
              
              mi['name'] = re.search(r'"name":"(.*?)",',data)
              mi['brand'] = re.search(r'"brand":"(.*?)",',data)
              mi['description'] = re.search(r'"description":"(.*?)",',data)
              mi['current_price'] = re.search(r'"price":"(.*?)",',data)
              mi['third_party_category_name'] = re.search(r'"category":"(.*?)",',data)
              mi['review_score'] = re.search(r'"ratingValue":"(.*?)",', data)
              mi['review_numbers'] = re.search(r'"reviewCount":"(.*?)",', data)
              mi['third_party_product_id'] = re.search(r'prod(\d+)\?',response.url)
              mi['original_price'] = response.xpath('//span[@class="price"]/text()').extract_first(default=None)
              
              for k in mi.copy():
                  if not mi[k] and mi[k] !=0:
                      del mi[k]
                  elif k == 'original_price':
                      mi[k] = float(mi[k].replace(',', '').strip('$'))
                  else:
                      mi[k] = mi[k].group(1)
                      if k == 'current_price':
                          mi[k] = float(mi[k].replace(',', '').strip('$'))
                      elif k == 'review_score':
                          mi[k] = float(mi[k])
                      elif k == 'review_numbers':
                          mi[k] = int(mi[k])
                          
                      
              mi['platform'] = 'NeimanMarcus'
              mi['third_party_type'] = 5
              mi['retailer'] = 'NeimanMarcus'
              mi['source_url'] = response.url
              
              exist = query_merch_item_info(mi['third_party_product_id'],mi['third_party_type'])
              if exist:
                  print('===== exist ,stop making pv =====')
                  mi['exist'] = 1
                  mi['id'] = exist.get('id')
                  yield mi
                  return
              else:
                  mi['id'] = generate_merch_item_gid()
                  yield mi
                  
                  imgs = re.findall(r'"large":{"url":"(.*?)",',response.text)
                  if not imgs:
                      logging.warning('==== imgs {}'.format(imgs))
                      return
                  
                  imgs = list(set(imgs))
                  for img in imgs:
                      pv = PvItem()
                      pv['pv_id'] = generate_pv_gid()
                      pv['media_type'] = 0
                      pv['url'] = 'item_total_images/neimanmarcus/{}/{}.jpg'.format(mi['id'], pv['pv_id'])
                      pv['description'] = mi.get('description')
                      pv['source'] = 6
                      pv['source_url'] = 'https:{}'.format(img)
                      pv['merch_item_id'] = mi['id']
                      handle_images(img=pv['source_url'], mid=mi['id'],
                                    storage_url=pv['url'].replace('item_total_images/', ''), bucket=self.bucket_name)
                      yield pv
          except Exception as e:
              traceback.print_exc()
              error_handle(e,traceback.print_exc())


      
  
      
