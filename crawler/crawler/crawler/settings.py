# -*- coding: utf-8 -*-

# Scrapy settings for crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 3

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  # 'Cookie':'viewNumR1=100; isPopupEnabledR1=true; pocketViewR1=front; sourcetracking=cj; currency=USD; currencyOverride=USD; originalsource=""; remarketing=TypeA; optimizelyEndUserId=oeu1557143465055r0.5654903954861774; _ga=GA1.2.1254899771.1557143466; SSP_AB_StyleFinder_20160425=Test; SSP_AB_StyleFinderPhase_20160425=Phase10; _fbp=fb.1.1557143468647.641649931; cto_lwid=610fd1e2-4b05-41a7-96a6-78bec28f3b05; rskxRunCookie=0; rCookie=3voham3iv5fmu06p9m43uc; _scid=ec872384-4d1a-4314-8322-e44cc1d1e18f; _sctr=1|1557072000000; __lc.visitor_id.7020571=S1557143470.1c5bcfc619; _sp_id.9084=b1127337-5b75-4b8c-9260-25d3f421725e.1557143466.1.1557143587.1557143466.8ef22489-3404-4b7b-bab6-fea3d43aa67c; sourcetrackingdate=1557201619397; visitor-cookie30=true; visitor-cookie1=true; fontsLoaded=1; countryCodePref=CN; userLanguagePref=en; userClosedNtfDialogCount=1; userLastSeenNtfDialogDate=2019-05-28; userSeenNtfDialogDate=2019-05-28; searchMobileFilterByR1=""; sizeFilterByR1=""; shoeSizeFilterByR1=""; topSizeFilterByR1=""; bottomSizeFilterByR1=""; handbagFilterByR1=""; heelFilterByR1=""; riseFilterByR1=""; colorFilterByR1=""; priceFilterByR1=""; percentFilterByR1=""; sortByR2=featured; Hm_lvt_cc77be0d75b2c4fd7cb3957beb973526=1559050986,1560676613; _gid=GA1.2.828115621.1560676614; lc_sso7020571=1560828383696; product-zoom-appeared=true; name.cookie.last.visited.product=HARL-WR57; JSESSIONID2=959114723F3827513E8AFC1DDFA19E38.tc-gouken_tomcat2; bb_PageURL=%2Fr%2FHomepage.jsp%3F%26d%3DMens%26navsrc%3Dmain; ntfPopupSuppressionCount=28; Hm_lpvt_cc77be0d75b2c4fd7cb3957beb973526=1560865644; browserID=bTO5SRD61q6bD27QPdhw3EDvChDGGd; lastRskxRun=1560865648887',
  'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'crawler.middlewares.crawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'crawler.ProxyMiddleware.ProxyMiddleware': 399,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'crawler.pipelines.GCSFilePipeline': 301,
    # 'crawler.pipelines.MyPipeline': 298,
    'crawler.pipelines.CrawlerPipeline': 302,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER_PERSIST = True
# REDIS_PARAMS = {
#     'db': 0,
#     'password':'1x2yxtabc'
# }
# REDIS_PROT = '6379'
# REDIS_HOST = '35.221.151.226'
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
# HTTPERROR_ALLOWED_CODES = [301,302,403,404,418,911,500,502,503]

#
# IMAGES_STORE = 'gs://amazon_image/'
# IMAGES_STORE_GCS_ACL = 'publicRead'
# GCS_PROJECT_ID = 'influneceforce'
