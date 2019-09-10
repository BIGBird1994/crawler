import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname('__file__'),os.path.pardir)))
sys.path.append(os.path.abspath(os.path.dirname('__file__')))
print(sys.path)




from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater




def sleep(*args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)

process = CrawlerProcess(get_project_settings())



def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print('waiting 5 minutes before restart...'))
    deferred.addCallback(sleep, seconds=5*60)
    deferred.addCallback(_crawl, spider)
    return deferred


_crawl(None, 'tp')
process.start()
        

