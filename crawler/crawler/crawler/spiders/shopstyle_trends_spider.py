# -*- coding: utf-8 -*-
import re
from json import loads
from logging import getLogger

from scrapy import Spider, Request

from ..id_util import *
from ..image_util import handle_images
from ..items import *
from ..query_util import *


class trends_people_spider(Spider):
    name = 'tp'
    url = 'https://www.shopstyle.com{}'
    api = 'https://www.shopstyle.com/api/v2/site/featuredLooks?offset={}&pid=shopstyle'
    author_api = 'https://www.shopstyle.com/api/v2/posts?maxNumProducts=100&offset={}&pid=shopstyle&userId={}'
    logger = getLogger(__name__)
    PageNum = 101
    filter_set = ['#ShopStyle', '#MyShopStyle', '#myshopstyle', '#ssCollective', '#ShopStyleCollective', '#shopthelook', '#stylesnap', '#style', '#shopstyle', '#sponsored', '#LooksChallenge']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'ITEM_PIPELINES': {
            'crawler.pipelines.CrawlerPipeline': 302,
        },
        'HTTPERROR_ALLOWED_CODES ': [301, 302, 403, 404, 418, 911, 500, 502, 503]
    }
    bucket_name = 'item_total_images'
    
    def start_requests(self):
        for i in range(self.PageNum):
            yield Request(url=self.api.format(i * 10), callback=self.parse, dont_filter=True)
    
    def parse(self, response):
        try:
            resp = loads(response.text)
            for data in resp['posts']:
                id = data['postUrl'].split('/')[-1]
                _exist = query_post_info(id)
                if not _exist:
                    print('===== crawl post {}'.format(data['postUrl']))
                    yield from self.parse_func(data)
                else:
                    print('===== {} exist {} \n update ===='.format(data['postUrl'], _exist))
                    influencer_post_id = _exist.get('id')
                    influencer_id = _exist.get('influencer_id')
                    media_url = _exist.get('media_url')
                    yield from self.update_func(data, influencer_post_id, influencer_id, media_url)
                
                name = data['postUrl'].split('/')[2]
                exist = query_influencer_info(name)
                if not exist:
                    print('===== crawl {} profile'.format(name))
                    yield Request(url=self.author_api.format(0, name), callback=self.parse_author_profile_post)
                else:
                    print('===== {} exist {}'.format(name, exist))
        
        except Exception as e:
            traceback.format_exc()
            error_handle(e, traceback.format_exc())
    
    def parse_author_profile_post(self, response):
        resp = loads(response.text)
        if resp.get('products') == [] or 'errorMessage' in response.text:
            return
        try:
            for data in resp['posts']:
                id = data['postUrl'].split('/')[-1]
                _exist = query_post_info(id)
                if not _exist:
                    print('==== crawl influencer new post')
                    yield from self.parse_func(data)
                else:
                    print('==== update influencer post')
                    influencer_post_id = _exist.get('id')
                    influencer_id = _exist.get('influencer_id')
                    media_url = _exist.get('media_url')
                    yield from self.update_func(data, influencer_post_id, influencer_id, media_url)
            
            offset = re.search(r'offset=(\d+)', response.url).group(1)
            next_page = re.sub('offset=\d+', 'offset={}'.format(int(offset) + 10), response.url)
            self.logger.info('<----- fetch next page {}------>'.format(next_page))
            yield Request(url=next_page, callback=self.parse_more_post)
        except Exception as e:
            traceback.format_exc()
            error_handle(e, traceback.format_exc())
    
    def update_func(self, data, influencer_post_id, influencer_id, media_url):
        try:
            ifp = InfluencerPlatformItem()
            ifpd = InfluencerPostDetailItem()
            
            ifp['influencer_id'] = influencer_id
            ifp['third_party_id'] = data['author']['handle']
            ifp['third_party_type'] = 2
            ifp['subject_type'] = 1
            ifp['country'] = data['author'].get('locale')
            ifp['name'] = data['author'].get('firstName') + ' ' + data['author'].get('lastName')
            
            ifp['follower_num'] = data['author']['favoriteCount']
            ifp['profile_picture_url'] = data['author']['image']
            if data.get('description', None):
                ifp['ins_username'] = re.findall(r'\@(\w+)', data.get('description'), re.S)
            if ifp.get('ins_username', None):
                ifp['ins_username'] = ifp['ins_username'][0]
            ifp['update'] = True
            
            ifpd['id'] = influencer_post_id
            ifpd['influencer_id'] = ifp['influencer_id']
            ifpd['media_source_url'] = 'https://www.shopstyle.com{}'.format(data['postUrl'])
            ifpd['media_type'] = 0
            ifpd['third_party_post_id'] = re.search(r'/(\d+)', data['postUrl']).group(1)
            ifpd['third_party_inf_id'] = ifp['third_party_id']
            ifpd['third_party_type'] = 2
            ifpd['post_content'] = data.get('description')
            ifpd['third_party_post_time'] = data['date']['date']
            l = []
            for d in data['taggedDescription']['messageTags']:
                if d['text'] not in self.filter_set:
                    l.append(d['text'])
            if len(l) > 0:
                ifpd['hashtags'] = ''.join(l)
            
            ifpd['likes_count'] = data.get('favoriteCount')
            ifpd['comments_count'] = data.get('commentCount')
            ifpd['views_count'] = 0
            ifpd['media_url'] = media_url
            
            ifpd['update'] = True
            yield ifpd
            yield ifp
            
            for d in data['products']:
                pmim = PostMerchItemMapItem()
                mi = MerchItemItem()
                mi['post_id'] = ifpd['id']
                mi['third_party_product_id'] = d.get('id')
                mi['third_party_type'] = 2
                mi['source_url'] = d.get('directUrl')
                mi['name'] = d.get('name')
                mi['original_price'] = d.get('price')
                if 'salePrice' not in d.keys():
                    mi['current_price'] = d.get('price')
                else:
                    mi['current_price'] = d.get('price')
                mi['description'] = d.get('description')
                mi['brand'] = d.get('brand').get('name')
                
                if d.get('retailer'):
                    mi['retailer'] = d.get('retailer').get('name')
                
                if d.get('categories'):
                    mi['third_party_category_name'] = d['categories'][0]['id']
                    mi['third_party_category_id'] = d['categories'][0]['numId']
                
                exist = query_merch_item_info(d['id'])
                if exist:
                    mi['id'] = exist.get('id')
                    mi['exist'] = 1
                    yield mi
                
                else:
                    mi['id'] = generate_merch_item_gid()
                    yield mi
                    
                    imgs = [d['image']['sizes']['Best']['url']]
                    for _ in d['alternateImages']:
                        imgs.append(_['sizes']['Best']['url'])
                    
                    if not imgs:
                        print('==== imgs {}, check this post later'.format(imgs))
                        return
                    
                    imgs = list(set(imgs))
                    for img in imgs:
                        pv = PvItem()
                        try:
                            pv['pv_id'] = generate_pv_gid()
                            pv['post_id'] = ifpd['id']
                            pv['media_type'] = 0
                            pv['url'] = 'item_total_images/shopstyle_post/{}/{}.jpeg'.format(mi['id'], pv['pv_id'])
                            pv['description'] = d.get('description')
                            pv['merch_item_id'] = mi['id']
                            pv['source'] = 3
                            pv['source_url'] = img
                            yield pv
                            handle_images(img=pv['source_url'], mid=mi['id'],
                                          storage_url=pv['url'].replace('item_total_images/', ''),
                                          bucket=self.bucket_name)
                        except Exception as e:
                            traceback.format_exc()
                            continue
                    
                    pmim['post_id'] = ifpd.get('id')
                    pmim['third_party_product_id'] = mi.get('third_party_product_id')
                    pmim['merch_item_id'] = mi.get('id')
                    pmim['third_party_category_name'] = mi.get('third_party_category_name')
                    pmim['third_party_category_id'] = mi.get('third_party_category_id')
                    pmim['third_party_type'] = 2
                    yield Request(url=self.url.format(data['postUrl']), meta={ 'pmim': pmim },
                                  callback=self.parse_match_items,
                                  dont_filter=True)
        except Exception as e:
            traceback.format_exc()
            error_handle(e, traceback.format_exc())
    
    def parse_func(self, data):
        try:
            ifp = InfluencerPlatformItem()
            ifpd = InfluencerPostDetailItem()
            
            exist = query_influencer_info(data['author']['handle'])
            if exist:
                ifp['influencer_id'] = exist.get('influencer_id')
                ifp['third_party_id'] = exist.get('third_party_id')
                ifp['update'] = True
            else:
                ifp['influencer_id'] = generate_influencer_gid()
                ifp['third_party_id'] = data['author']['handle']
            
            ifp['third_party_type'] = 2
            ifp['subject_type'] = 1
            ifp['country'] = data['author'].get('locale')
            
            if 'firstName' and 'lastName' in data['author'].keys():
                ifp['name'] = data['author'].get('firstName') + ' ' + data['author'].get('lastName')
            
            ifp['follower_num'] = data['author']['favoriteCount']
            ifp['profile_picture_url'] = data['author']['image']
            if data.get('description', None):
                ifp['ins_username'] = re.findall(r'\@(\w+)', data.get('description'), re.S)
            if ifp.get('ins_username', None):
                ifp['ins_username'] = ifp['ins_username'][0]
            
            pv = PvItem()
            pv['pv_id'] = generate_pv_gid()
            pv['media_type'] = 0
            pv['url'] = 'item_total_images/shopstyle_post/{}/{}.jpeg'.format(data['author']['handle'], pv['pv_id'])
            pv['source'] = 3
            pv['description'] = data['author'].get('description')
            pv['source_url'] = data['author'].get('image')
            yield pv
            
            handle_images(img=pv['source_url'], mid=data['author']['handle'],
                          storage_url=pv['url'].replace('item_total_images/', ''), bucket=self.bucket_name)
            
            ifpd['id'] = generate_post_gid()
            ifpd['influencer_id'] = ifp['influencer_id']
            ifpd['media_source_url'] = 'https://www.shopstyle.com{}'.format(data['postUrl'])
            ifpd['media_type'] = 0
            ifpd['third_party_post_id'] = re.search(r'/(\d+)', data['postUrl']).group(1)
            ifpd['third_party_inf_id'] = ifp['third_party_id']
            ifpd['third_party_type'] = 2
            ifpd['post_content'] = data.get('description')
            ifpd['third_party_post_time'] = data['date']['date']
            l = []
            for d in data['taggedDescription']['messageTags']:
                if d['text'] not in self.filter_set:
                    l.append(d['text'])
            if len(l) > 0:
                ifpd['hashtags'] = ''.join(l)
            
            ifpd['likes_count'] = data.get('favoriteCount')
            ifpd['comments_count'] = data.get('commentCount')
            ifpd['views_count'] = 0
            ifpd['media_url'] = 'item_total_images/shopstyle_post/{}/{}.jpeg'.format(data['author']['handle'],
                                                                                     pv['pv_id'])
            yield ifpd
            yield ifp
            
            pv = PvItem()
            pv['pv_id'] = generate_pv_gid()
            pv['post_id'] = ifpd['id']
            pv['media_type'] = 0
            pv['url'] = 'item_total_images/shopstyle_post/{}/{}.jpeg'.format(data['author']['handle'], pv['pv_id'])
            pv['source'] = 3
            pv['description'] = data.get('description')
            pv['source_url'] = data['images'][0]['sizes']['Large']['url']
            yield pv
            handle_images(img=pv['source_url'], mid=data['author']['handle'],
                          storage_url=pv['url'].replace('item_total_images/', ''), bucket=self.bucket_name)
            
            for d in data['products']:
                pmim = PostMerchItemMapItem()
                mi = MerchItemItem()
                __exist = query_merch_item_info(d['id'])
                if __exist:
                    pmim['post_id'] = ifpd['id']
                    pmim['third_party_product_id'] = __exist.get('third_party_product_id')
                    pmim['merch_item_id'] = __exist.get('id')
                    pmim['third_party_category_id'] = __exist.get('third_party_category_id')
                    pmim['third_party_category_name'] = __exist.get('third_party_category_name')
                    pmim['third_party_type'] = 2
                    yield Request(url=self.url.format(data['postUrl']), meta={ 'pmim': pmim },
                                  callback=self.parse_match_items,
                                  dont_filter=True)
                else:
                    mi['id'] = generate_merch_item_gid()
                    mi['post_id'] = ifpd['id']
                    mi['third_party_product_id'] = d.get('id')
                    mi['third_party_type'] = 2
                    mi['source_url'] = d.get('directUrl')
                    mi['name'] = d.get('name')
                    mi['original_price'] = d.get('price')
                    if 'salePrice' not in d.keys():
                        mi['current_price'] = d.get('price')
                    else:
                        mi['current_price'] = d.get('price')
                    
                    mi['description'] = d.get('description')
                    
                    if d.get('brand'):
                        mi['brand'] = d.get('brand').get('name')
                    
                    if d.get('retailer'):
                        mi['retailer'] = d.get('retailer').get('name')
                    
                    if d.get('categories'):
                        mi['third_party_category_name'] = d['categories'][0]['id']
                        mi['third_party_category_id'] = d['categories'][0]['numId']
                    yield mi
                    
                    imgs = [d['image']['sizes']['Best']['url']]
                    for _ in d['alternateImages']:
                        imgs.append(_['sizes']['Best']['url'])
                    
                    if not imgs:
                        print('==== imgs {}, check this post later'.format(imgs))
                        return
                    imgs = list(set(imgs))
                    for img in imgs:
                        pv = PvItem()
                        try:
                            pv['pv_id'] = generate_pv_gid()
                            pv['post_id'] = ifpd['id']
                            pv['media_type'] = 0
                            pv['url'] = 'item_total_images/shopstyle_post/{}/{}.jpeg'.format(mi['id'], pv['pv_id'])
                            pv['description'] = d.get('description')
                            pv['merch_item_id'] = mi['id']
                            pv['source'] = 3
                            pv['source_url'] = img
                            yield pv
                            handle_images(img=pv['source_url'], mid=mi['id'],
                                          storage_url=pv['url'].replace('item_total_images/', ''),
                                          bucket=self.bucket_name)
                        except Exception as e:
                            traceback.format_exc()
                            continue
                    pmim['post_id'] = ifpd.get('id')
                    pmim['third_party_product_id'] = mi.get('third_party_product_id')
                    pmim['merch_item_id'] = mi['id']
                    pmim['third_party_category_name'] = mi.get('third_party_category_name')
                    pmim['third_party_category_id'] = mi.get('third_party_category_id')
                    pmim['third_party_type'] = 2
                    yield Request(url=self.url.format(data['postUrl']), meta={ 'pmim': pmim },
                                  callback=self.parse_match_items,
                                  dont_filter=True)
                    continue
        except Exception as e:
            traceback.format_exc()
            error_handle(e, traceback.print_exc())
    
    def parse_match_items(self, response):
        try:
            pmim = response.meta['pmim']
            match_ids = []
            for data in response.xpath('//div[@class="product-cell__exact-match mat-body u-text-center ng-star-inserted"]/preceding-sibling::meta'):
                match_ids.append(int(data.xpath('./@product-id').extract_first()))
            if pmim['third_party_product_id'] not in match_ids:
                pmim['is_exact_match'] = 0
            else:
                pmim['is_exact_match'] = 1
            yield pmim
        except Exception as e:
            traceback.format_exc()
            error_handle(e, traceback.format_exc())
