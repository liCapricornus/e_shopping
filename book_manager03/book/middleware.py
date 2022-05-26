"""
    Django中的中间件是一个轻量级、底层的插件系统，可以介入Django的请求和响应处理过程，
修改Django的输入或输出。中间件的设计为开发者提供了一种无侵入式的开发方式，增强了Django框架的健壮性。
    我们可以使用中间件，在Django处理视图的不同阶段对输入或输出进行干预。
"""
from django.utils.deprecation import MiddlewareMixin
class TestMiddleWare(MiddlewareMixin):

    def process_request(self,request):
        print('每次请求前都要调用执行！')

        username = request.COOKIS.get('name')
        if username is None:
            print('没有用户信息！')
        else:
            print('有用户信息！')

    def process_response(self,request,response):
        print("每次响应前都会调用执行！")

        return response


