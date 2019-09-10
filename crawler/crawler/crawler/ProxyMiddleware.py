from .fetch_proxy import FetchProxy
import logging


class ProxyMiddleware(object):
    f = FetchProxy()

    def process_request(self, request, spider):
        if 'images-na.ssl-images-amazon' in request.url or 'googleapis' in request.url :
            logging.info('==== pass url {}'.format(request.url))
            return
        proxy = self.f.fetch_proxy()
        if not proxy:
            return
        request.meta["proxy"] = proxy
        logging.info('==== req using proxy {}'.format(proxy))
        
