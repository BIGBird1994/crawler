# -*- coding: utf-8 -*-

from scrapy import Request, Spider
from ..err_monitor import error_handle
from ..items import *
from ..id_util import *
import logging
import re
import traceback
import os
import datetime
import logging

from ..database import connection
from ..image_util import handle_images
from ..query_util import query_merch_item_info




class spider(Spider):
    name = 'ams'
    base_url = 'https://www.amazon.com/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8'
    custom_settings = {
        'CONCURRENT_REQUESTS': 10,
        'DOWNLOAD_TIMEOUT': 20,
        'ITEM_PIPELINES': {
            'crawler.pipelines.CrawlerPipeline': 302,
        },
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER_PERSIST': True,
        'REDIS_PARAMS': {
            'db': 1,
            'password': '1x2yxtabc'
        },
        'REDIS_PROT': '6379',
        'REDIS_HOST': '35.221.151.226',
        'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.SpiderPriorityQueue',
        'HTTPERROR_ALLOWED_CODES ': [301, 302, 403, 404, 418, 911, 500, 502, 503]
    }
    
    sql = """
            select id,third_party_product_id,third_party_type
            from merch_item mi where third_party_type=4
          """
    
    
    
    def start_requests(self):
        
        try:
            with connection.cursor() as cur:
                cur.execute(self.sql)
                ret = cur.fetchone()
                while ret:
                        if len(ret) !=3:
                            del ret
                        url = self.base_url.format(product_id=ret[1])
                        yield Request(url, callback=self.parse, meta={
                            'merch_item_id': ret[0],
                            'third_party_product_id': ret[1],
                            'third_party_type': ret[2]}, dont_filter=True)
                        ret = cur.fetchone()
            connection.close()
        except Exception as e:
            traceback.format_exc()
            error_handle(e,traceback.format_exc())

    
    
            
    def parse(self, response):
        
        try:
            merch_item_id = response.meta['merch_item_id']
            third_party_product_id = response.meta['third_party_product_id']
            third_party_type = response.meta['third_party_type']
            
            for data in response.xpath('//div[@id="cm_cr-review_list"]/div'):
                item = ReviewItem()
                item['review_id'] = data.xpath('./@id').extract_first(default=None)
                if not item.get('review_id'):
                    return
                item['author_name'] = data.xpath('.//span[@class="a-profile-name"]/text()').extract_first(default=None)
                item['review_score'] = data.xpath('.//span[@class="a-icon-alt"]/text()').extract_first(default=None)
                
                if item.get('review_score'):
                    try:
                        item['review_score'] = float(re.search(r'(\d\.\d)', item['review_score']).group(1))
                    except Exception as e:
                        traceback.format_exc()
                
                item['merch_item_id'] = merch_item_id
                item['third_party_product_id'] = third_party_product_id
                item['third_party_type'] = third_party_type
                item['platform'] = 'Amazon'
                item['publish_time'] = data.xpath('.//span[@class="a-size-base a-color-secondary review-date"]/text()').\
                    extract_first(default=None)
                content = data.xpath('.//span[@class="a-size-base review-text review-text-content"]//text()').extract()
                if content:
                    item['content'] = ''.join(content)
                yield (item)
                
            next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first(default=None)
            if next_page:
                logging.info('==== fetch next {}'.format(next_page))
                url = 'https://www.amazon.com{}'.format(next_page)
                yield Request(url=url,callback=self.parse,errback=self.err_handle,meta={
                   'merch_item_id':merch_item_id,
                   'third_party_product_id':third_party_product_id,
                   'third_party_type':third_party_type
                })
                return
            logging.warning('=== get next_page fail,{}'.format(response.url))
            
        except Exception as e:
            traceback.format_exc()
            error_handle(e,traceback.format_exc())
            
            
    
            
    def err_handle(self, failure):
        logging.warning('==== time out req')
        url = failure.request.url
        yield Request(url=url,callback=self.parse,meta=failure.request.meta)
    
