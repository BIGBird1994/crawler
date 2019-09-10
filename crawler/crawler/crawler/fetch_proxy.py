# encoding=utf-8
from redis import StrictRedis
import requests
import logging


class FetchProxy(object):

    proxy_api = 'http://webapi.http.zhimacangku.com/getip?num=10&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    r = StrictRedis(host='35.221.151.226',port=6379,password="1x2yxtabc",db=0)
    

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





