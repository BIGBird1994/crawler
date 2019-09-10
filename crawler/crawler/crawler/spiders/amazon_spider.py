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



from ..image_util import handle_images
from ..query_util import query_merch_item_info





class spider(Spider):
      name = 'aps'
      start_urls = [
          'https://www.amazon.com/s/browse?_encoding=UTF8&node=16225018011&ref_=nav_shopall-export_nav_mw_sbd_intl_womenfasion'
      ]
      url = 'https://www.amazon.com{}'
      _url = 'https://images-na.ssl-images-amazon.com/images/I/{}._UL1500_.jpg'
      custom_settings = {
          'CONCURRENT_REQUESTS' : 5,
          'DOWNLOAD_TIMEOUT': 20,
          'CRAWLERA_ENABLED' : True,
          'CRAWLERA_APIKEY' : 'd9cf91e3769041049a38554ba605f73a',
          'DOWNLOADER_MIDDLEWARES':{
          'scrapy_crawlera.CrawleraMiddleware': 610
      },
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
      brand_pattern = [
             '//a[@id="bylineInfo"]/text()',
             '//a[@id="brand"]/@href',
             '//td[@class="a-span7 a-size-base"]/text()',
      ]
      
      
      
      def start_requests(self):
          yield Request(self.start_urls[0],callback=self.parse,dont_filter=True)

        

          
      def parse(self, response):
          if 'Enter the characters you see below' in response.text or not response.status == 200:
              error_handle(err_msg='==== spider blocked',err_path=response.text)
              yield Request(url=response.url,callback=self.parse,dont_filter=True)
              
          
          for data in response.xpath('//a[@class="a-link-normal acs_tile__title-image aok-block a-text-normal"]'):
              href = data.xpath('./@href').extract_first(default=None)
              yield Request(url=self.url.format(href),callback=self.parse_sub_cate,dont_filter=True)
              
              
      def parse_sub_cate(self, response):
          
          if (response.meta).get('msg') is not None:
              for data in response.xpath('//li[@class="a-spacing-micro s-navigation-indent-2"]/span/a'):
                  href = data.xpath('./@href').extract_first(default=None)
                  yield Request(url=self.url.format(href), callback=self.parse_page_list)
                  return

          for data in response.xpath('//li[@class="a-spacing-micro s-navigation-indent-2"]/span/a'):
              href = data.xpath('./@href').extract_first(default=None)
              yield Request(url=self.url.format(href),meta={'msg':'parse_sub'},callback=self.parse_sub_cate)
          
      
      def parse_page_list(self, response):
    
          if 'Enter the characters you see below' in response.text or not response.status == 200:
              error_handle(err_msg='==== spider blocked {}'.format(response.url), err_path=response.status)
              yield Request(url=response.url, callback=self.parse_page_list, dont_filter=True)

          for data in response.xpath('//a[@class="a-link-normal a-text-normal"]')[2:]:
              href = data.xpath('./@href').extract_first(default=None)
              yield Request(url=self.url.format(href), callback=self.parse_detail)

              
          next_page = response.xpath('//li[@class="a-last"]/a/@href').extract()
          if not next_page:
              logging.warning('===== page {}'.format(next_page))
              error_handle(err_msg='amazon turn page done or fail {}'.format(response.url),err_path='line 111')
              return
          logging.info('===== fetch next {}'.format(next_page))
          yield Request(url=self.url.format(next_page[0]),callback=self.parse_page_list,errback=self.error_handle)
         
          
          
      def parse_detail(self, response):
          if 'Enter the characters you see below' in response.text or not response.status == 200:
              error_handle(err_msg='==== spider blocked {}'.format(response.url), err_path=response.status)
              yield Request(url=response.url, callback=self.parse_detail, dont_filter=True)
          
       
          try:
              mi = MerchItemItem()
              mi['name'] = response.xpath('//span[@id="productTitle"]/text()').extract_first(default=None)
              if mi.get('name') is not None:
                 mi['name'] = mi['name'].strip()
                  
              price = response.xpath('//span[@id="priceblock_ourprice"]/text()').extract_first(default=None)
              
              if price:
                 price = price.replace('CA','').replace('€','')
                 
              if price and '-' in price:
                  mi['min_price'] = float((re.sub(r'\n|\$| ','',price.split('-')[0])).replace(',',''))
                  mi['max_price'] = float((re.sub(r'\n|\$| ','',price.split('-')[-1])).replace(',',''))
              elif price:
                  mi['current_price'] = float(price.replace(',','').strip('$'))
              
              mi['price_range'] = response.xpath('//span[@id="priceblock_ourprice"]/text()').extract_first(default=None)
              if  mi.get('price_range'):
                  if '-' not in mi['price_range']:
                      mi['price_range'] = None
                      
              mi['original_price'] = response.xpath('//span[@class="priceBlockStrikePriceString a-text-strike"]/text()').extract_first(default=None)
              
              if mi.get('original_price'):
                  try:
                    mi['original_price'] = float(mi['original_price'].replace(',','').replace('$',''))
                  except Exception as e:
                      traceback.print_exc()
                      mi['original_price'] = None
                  
              if not mi.get('current_price') and mi.get('original_price'):
                  mi['current_price'] = response.xpath('//span[@id="priceblock_pospromoprice"]/text()').extract_first(default=None)
                  if mi.get('curren_price'):
                      mi['current_price'] = float(mi['current_price'].replace(',','').replace('$',''))
                      
              if not mi.get('current_price'):
                  mi['current_price'] = response.xpath('//div[@id="olp-upd-new"]/span[1]//text()').extract_first(default=None)
                  if mi.get('curren_price'):
                      mi['current_price'] = float(mi['current_price'].replace(',','').replace('$',''))
                      
              for p in self.brand_pattern:
                 if isinstance(response.xpath(p).extract_first(),str):
                      mi['brand'] = response.xpath(p).extract_first().strip()
                      if '/' in mi['brand'] and len(mi['brand']) > 20:
                            mi['brand'] = mi['brand'].split('/')[1]
                  
              details = response.xpath('//ul[@class="a-unordered-list a-vertical a-spacing-none"]/li/span//text()').extract()
              if not details:
                  details = response.xpath('//ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none"]/li/span//text()').extract()
                  logging.warning('===== details {},{}'.format(details,response.url))
              else:
                  details = re.sub(r'(\n|\t)', '', (';'.join(details)))
              mi['description'] = details
              mi['platform'] = 'Amazon'
              mi['third_party_type'] = 4
              mi['retailer'] = 'Amazon'
              mi['source_url'] = response.url
              category_name = (''.join(response.xpath('//ul[@class="a-unordered-list a-horizontal a-size-small"]//text()').extract()))
              mi['third_party_category_name'] = re.sub(r'\n|\t|\r|  ', '', category_name)
              mi['third_party_product_id'] = re.search(r'dp/(.*?)/', response.url).group(1)
              mi['review_numbers'] = response.xpath('//span[@id="acrCustomerReviewText"]/text()').extract_first(default=None)
             
              if mi.get('review_numbers'):
                  try:
                    mi['review_numbers'] = int(re.search(r'(\d+)',mi['review_numbers'].replace(',','')).group(1))
                  except Exception as e:
                      traceback.format_exc()
             
              if not isinstance(mi.get('review_numbers'), int):
                  mi['review_numbers'] = None
                  
              mi['review_score'] = response.xpath('//span[@class="a-icon-alt"]/text()').extract_first(default=None)
              if mi.get('review_score'):
                  try:
                    mi['review_score'] = float(re.search(r'(\d\.\d)',mi['review_score']).group(1))
                  except Exception as e:
                      traceback.format_exc()
              
              if not isinstance(mi.get('review_score'), float):
                  mi['review_score'] = None
                  
              exist = query_merch_item_info(mi['third_party_product_id'],mi['third_party_type'])
              if exist:
                  print('===== exist ,stop making pv')
                  mi['exist'] = 1
                  mi['id'] = exist.get('id')
                  yield mi
                  return
              else:
                  mi['id'] = generate_merch_item_gid()
                  yield mi
                  imgs = response.xpath('//img[@class="imgSwatch"]/@src').extract()
                  if not imgs:
                      logging.warning('==== imgs {}'.format(imgs))
                      return
                  imgs = list(set(imgs))
                  for img in imgs:
                      
                          pv = PvItem()
                          pv['pv_id'] = generate_pv_gid()
                          pv['media_type'] = 0
                          pv['url'] = 'item_total_images/amazon/{}/{}.jpg'.format(mi['id'], pv['pv_id'])
                          pv['description'] = mi.get('description')
                          pv['source'] = 5
                          pv['source_url'] = self._url.format(re.search(r'images/I/(.*?)\._', img).group(1))
                          pv['merch_item_id'] = mi['id']
                          yield (pv)
                          handle_images(img=pv['source_url'], mid=mi['id'], storage_url=pv['url'].replace('item_total_images/',''), bucket=self.bucket_name)
                      
          except Exception as e:
              traceback.format_exc()
              error_handle('{},{}'.format(e,response.url), traceback.format_exc())


                
                
                
      def error_handle(self, failure):
          url = failure.request.url
          logging.info('===== handle fail url {}'.format(url))
          yield Request(url=url,callback=self.parse_page_list,dont_filter=True)
          
          
          
      



          
          
              
              