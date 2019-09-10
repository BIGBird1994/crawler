from scrapy import Request,Spider
from ..err_monitor import error_handle
from ..items import MerchItemItem,PvItem
from ..id_util import *
import logging
import re
import traceback
from ..image_util import handle_images
from ..query_util import query_merch_item_info



class spider(Spider):
      crawlera_enabled = True
      crawlera_apikey = 'd9cf91e3769041049a38554ba605f73a'
      name = 'rps'
      start_urls = [
          'https://www.revolve.com/clothing/br/3699fc/?navsrc=main',
          'https://www.revolve.com/shoes/br/3f40a9/?navsrc=main',
          'https://www.revolve.com/jewelry-accessories/br/946fac/?navsrc=main',
          'https://www.revolve.com/mens/accessories/br/8ad9de/?navsrc=main',
          'https://www.revolve.com/mens/shoes/br/b05f2e/?navsrc=main',
          'https://www.revolve.com/mens/clothing/br/15d48b/?navsrc=main'
      ]
      url = 'https://www.revolve.com{}'
      api = 'https://www.revolve.com/r/BrandsContent.jsp?{}&pageNum={}&pageNum={}'
      params_map = {
          'clothing' : '&aliasURL=clothing/br/3699fc&s=c&c=Clothing&navsrc=main',
          'shoes' : '&aliasURL=shoes/br/3f40a9&s=c&c=Shoes&navsrc=main',
          'jewelry-accessories' : '&aliasURL=jewelry-accessories/br/946fac&s=c&c=Jewelry+&+Accessories&navsrc=main',
          'mensclothing': '&aliasURL=mens/clothing/br/15d48b&s=c&c=Clothing&d=Mens&navsrc=main',
          'mensshoes' : '&aliasURL=mens/shoes/br/b05f2e&s=c&c=Shoes&d=Mens&navsrc=main',
          'mensaccessories' : '&aliasURL=mens/accessories/br/8ad9de&s=c&c=Accessories&d=Mens&navsrc=main'
      }
      bucket_name = 'item_total_images'
      custom_settings = {
          'CRAWLERA_ENABLED': True,
          'CRAWLERA_APIKEY': 'd9cf91e3769041049a38554ba605f73a',
          'DOWNLOADER_MIDDLEWARES': {
              'scrapy_crawlera.CrawleraMiddleware': 610
          },
          'ITEM_PIPELINES': {
              'crawler.pipelines.CrawlerPipeline': 302,
          },
          # 'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
          # 'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
          # 'SCHEDULER_PERSIST': True,
          # 'REDIS_PARAMS': {
          #     'db': 0,
          #     'password': '1x2yxtabc'
          # },
          # 'REDIS_PROT': '6379',
          # 'REDIS_HOST': '35.221.151.226',
          # 'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.SpiderPriorityQueue',
          # 'HTTPERROR_ALLOWED_CODES ': [301, 302, 403, 404, 418, 911, 500, 502, 503]
      }

      
      def parse(self, response):
          try:
              for data in response.xpath('//a[@class="js-plp-pdp-link plp__image-link "]'):
                  href = data.xpath('./@href').extract_first()
                  yield Request(url=self.url.format(href), callback=self.parse_detail)
              
              page_num = response.xpath('//a[@class="pagination__link  "]/text()').extract()
              if not page_num:
                  return
              page_num = int(page_num[-1])
              
              if 'mens' in response.url:
                  c_name = ''.join(response.url.split('/')[3:4])
                  param = self.params_map.get(c_name)
                  for i in range(2, page_num + 1):
                      yield Request(url=self.api.format(param, i, i), callback=self.parse_list)
              
              else:
                  c_name = ''.join(response.url.split('/')[3])
                  param = self.params_map.get(c_name)
                  for i in range(2,page_num + 1):
                      yield Request(url=self.api.format(param,i,i),callback=self.parse_list)
          except Exception as  e:
              print(e)
              error_handle(e,traceback.format_exc())

              
              
      def parse_list(self, response):
          try:
              if 'No products found' in response.text:
                  print('=== no products')
                  return
              for data in response.xpath('//a[@class="js-plp-pdp-link plp__image-link "]'):
                  href = data.xpath('./@href').extract_first()
                  yield Request(url=self.url.format(href), callback=self.parse_detail)
          except Exception as e:
              print(e)
              error_handle(e,traceback.format_exc())

              
              
      def parse_detail(self, response):
          try:
              mi = MerchItemItem()

              mi['name'] = response.xpath('//h1[@class="product-name--lg u-text-transform--none u-margin-t--none u-margin-b--sm"]/text()').extract_first(default=None)
              # mi['name'] = re.sub(r'\n|\t| ','',name)
              mi['third_party_product_id'] = re.search(r'dp/(.*?)/',response.url).group(1)
              o_p = response.xpath('//span[@id="retailPrice"]/text()').extract_first(default=None)
              if o_p:
                  o_p = re.sub(r'\n|\$| ','',o_p)
                  mi['original_price'] = float(o_p.replace(',',''))
              c_p = (response.xpath('//span[@id="markdownPrice"]/text()').extract_first(default=None))
              if c_p:
                  c_p = re.sub(r'\n|\$| ','',c_p)
                  mi['current_price'] = float(c_p.replace(',',''))
              mi['description'] = '\n'.join(response.xpath('//ul[@class="product-details__list u-margin-l--none"]/li/text()').extract())
              mi['platform'] = 'Revolve'
              mi['third_party_type'] = 3
              brand = response.xpath('//div[@class="product-brand"]/text()').extract()
              if brand:
                  mi['brand'] = re.sub(r'\n|\t| ','',brand[0])
              mi['retailer'] = 'Revolve'
              mi['source_url'] = response.url
              category_name = (''.join(response.xpath('//li[@property="itemListElement"]//text()').extract()))
              mi['third_party_category_name'] = re.sub(r'\n|\t|\r|  ','',category_name)
              
              exist = query_merch_item_info(mi['third_party_product_id'])
              if exist:
                  print('==== exist stop making pv item')
                  mi['exist'] = 1
                  mi['id'] = exist.get('id')
                  yield mi
                  return
              else:
                  mi['id'] = generate_merch_item_gid()
                  yield mi
                  imgs = response.xpath('//div[@class="slideshow__pager"]/a/@data-image').extract()
                  if not imgs:
                      error_handle(err_msg='{} ,has no images'.format(response.url), err_path='')
                      return
                  imgs = list(set(imgs))
                  for img in imgs:
                      
                          pv = PvItem()
                          pv['pv_id'] = generate_pv_gid()
                          pv['media_type'] = 0
                          pv['url'] = 'item_total_images/revolve/{}/{}.jpeg'.format(mi['id'], pv['pv_id'])
                          pv['description'] = mi.get('description')
                          pv['source'] = 4
                          pv['source_url'] = img
                          pv['merch_item_id'] = mi['id']
                          yield (pv)
                          handle_images(img=pv['source_url'], mid=mi['id'], storage_url=pv['url'].replace('item_total_images/',''), bucket=self.bucket_name)
                      
          
          except Exception as e:
              print(e)
              error_handle(e,traceback.format_exc())