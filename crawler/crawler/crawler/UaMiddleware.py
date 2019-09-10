from user_agent import generate_user_agent



class UaMiddleware(object):


    def process_request(self, request, spider):
        ua = generate_user_agent()
        print('==== using {}'.format(ua))
        request.meta['User-Agent'] = ua

