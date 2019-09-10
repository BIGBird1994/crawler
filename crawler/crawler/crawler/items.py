# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field,Item


class ShopstyleItem(Item):
      json_info = Field()
      category_link = Field()
      category_name = Field()
      source_url = Field()
      post_id = Field()
      json_obj = Field()
      id = Field()
      product_id = Field()
      
      

class PvItem(Item):
      pv_id = Field()
      media_type = Field()
      post_id = Field()
      url = Field()
      description = Field()
      source = Field()
      source_url = Field()
      images = Field()
      merch_item_id = Field()
      
      
class MerchItemItem(Item):
      id = Field()
      platform = Field()
      third_party_product_id = Field()
      source_url = Field()
      post_id = Field()
      name = Field()
      current_price = Field()
      original_price = Field()
      description = Field()
      brand = Field()
      retailer = Field()
      third_party_type = Field()
      third_party_category_id = Field()
      third_party_category_name = Field()
      price = Field()
      exist = Field()
      min_price = Field()
      max_price = Field()
      price_range = Field()
      # review_detail = Field()
      review_numbers = Field()
      review_score = Field()


class ReviewItem(Item):
      review_score = Field()
      publish_time = Field()
      content = Field()
      author_name = Field()
      third_party_product_id = Field()
      third_party_type = Field()
      merch_item_id = Field()
      platform = Field()
      review_id = Field()


class InfluencerPlatformItem(Item):
      influencer_id = Field()
      third_party_id = Field()
      third_party_type = Field()
      name = Field()
      follower_num = Field()
      profile_picture_url = Field()
      ins_username = Field()
      subject_type = Field()
      country = Field()
      update = Field()
      


class InfluencerPostDetailItem(Item):
      id = Field()
      influencer_id = Field()
      media_source_url = Field()
      media_type = Field()
      media_url = Field()
      third_party_post_id = Field()
      third_party_inf_id = Field()
      third_party_type = Field()
      post_content = Field()
      third_party_post_time = Field()
      hashtags = Field()
      likes_count = Field()
      comments_count = Field()
      views_count = Field()
      update = Field()

      
      
class PostMerchItemMapItem(Item):
      id = Field()
      product_id = Field()
      post_id = Field()
      third_party_type = Field()
      third_party_category_id = Field()
      third_party_category_name = Field()
      is_exact_match = Field()
      merch_item_id = Field()
      third_party_product_id = Field()
      
      
