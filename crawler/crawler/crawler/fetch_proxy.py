# encoding=utf-8
from redis import StrictRedis
import requests
import logging


class FetchProxy(object):

    proxy_api = ''
    r = StrictRedis(host='35.221.151.226',port=6379,password="123",db=0)
    

    def get_proxy(self):
        logging.info("===== get proxy")
        try:
            resp = requests.get(self.proxy_api)
            proxy = resp.text
            proxy_list = proxy.split('\r\n')[:-1]
            if proxy_list is not None:
               return proxy_list
        except Exception as e:
            print(e)


    def test_proxy(self,proxy_list):
        try:
            for p in proxy_list:
                   proxy = "https://{}".format(p)
                   self.r.lpush("zhima_proxy",proxy)
                   print('==== save to redis')
        except :
            print("===== fail")


    def count_proxy(self):
        return self.r.llen("zhima_proxy")
    

    def fetch_proxy(self):
        proxy = self.r.lpop("zhima_proxy")
        if proxy is not None and self.r.llen("zhima_proxy") > 10:
           return proxy.decode(encoding="utf-8")
        else:
            print('===== need to fetch proxy!!')
            self.main()



    def save_proxy(self,proxy):
        self.r.rpush("zhima_proxy",proxy)


    
    
    @classmethod
    def main(self):
        f = FetchProxy()
        while f.count_proxy() == None or f.count_proxy() < 50:
                proxy_list = f.get_proxy()
                f.test_proxy(proxy_list)
                print("already fetch %s" % f.count_proxy())
        print(f.count_proxy())


if __name__ == '__main__':
     FetchProxy().main()





