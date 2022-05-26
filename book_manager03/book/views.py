from django.http import HttpResponse
from django.shortcuts import render, redirect

from book.models import BookInfo

# Create your views here.

def create_book(request):

    book = BookInfo.objects.create(
        name='AI0525',
        pub_date='1996-2-14',
        readcount=10,
        commentcount=99,
        is_delete=True,
    )

    return HttpResponse('create')

def shop(request,city_id,mobile):

    # import re
    # if not re.match('\d{5}',shop_id):
    #     return HttpResponse('没有此商品！')

    print(city_id, mobile)  # 会在run框打印 url的11000/11004

    query_params = request.GET
    print(query_params)  # 打印出 {order:[readcount]}
    # <QueryDict: {'order': ['readcount']}> 具有字典的特性还具有一键多值

    order = query_params.getlist('order')  # git只能获取一个value
    print(order)  # 打印出 readcount

    return HttpResponse('请不要在RPG游戏入戏太深，起码今天是这样.')

"""
查询字符串
    http://ip:port/path/path/?key=value&key1=value1
    请求路径 + ？+ 查询字符串（类似于字典）并采用&连接
"""

def register(request):

    data = request.POST  # JSON不能通过request.POST获取数据
    print(data)
    # <QueryDict: {'username': ['lishao'], 'password': ['1024']}>

    return HttpResponse('OK')

def json(request):

    body = request.body
    # print(body)
    # b'{\n    "name":"lishao",\n    "age":"25"\n}'
    body_str = body.decode()
    # print(body_str)  # str格式
    """
    {
    "name":"lishao",
    "age":"25"
    }
    """
    # JSON形式的字符串可以转换为python的字典
    import json
    body_dict = json.loads(body_str)
    # print(body_dict)
    # {'name': 'lishao', 'age': '25'}

    # 请求头
    # print(request.META)
    print(request.META['SERVER_PORT'])

    return HttpResponse('json')

def method(request):

    print(request.method)

    return HttpResponse('method')

from django.http import HttpResponse,JsonResponse
def response(request):

    # response = HttpResponse('res',status=102)
    #
    # response['name']='lishao'
    #
    # return response

    # 响应状态码 1xx 2xx 3xx 4xx 5xx --- 100-599
    # 404 路由有问题  403 禁止访问（权限问题） 400 200 成功
    info = {
        'name':'鬼泣哥',
        'address':'beijing'
    }
    girl_friends = [
        {
            'name': 'lhc',
            'address': 'beijing'
        },
        {
            'name': 'ls',
            'address': 'dnf'
        }
    ]
    # data 返回的响应数据一般是字典类型
    # safe = True 表示我们的data是字典数据
    # response = JsonResponse(data=girl_friends, safe=False)
    #
    # return response

    # return redirect('http://www.4399.com')

    import json
    # data = json.dumps(data, cls=encoder, **json_dumps_params)
    data = json.dumps(girl_friends)

    response = HttpResponse(data)
    return response

"""
    Cookie & Session
        http://127.0.0.1:8000/set_cookie/username=lishao&password=1024
    第一次：服务器接受到请求后，获取username，服务器设置cookie信息
        浏览器接收到服务器的响应后，应该把cookie保存
    第二次及以后：访问http://127.0.0.1:8000 都会携带cookie信息
        同时服务器读取cookie信息，来判断用户身份。
"""


def set_cookie(request):
    # 1.获取查询字符串数据
    username = request.GET.get('username')
    password = request.GET.get('password')
    # 2.服务器设置cookie信息

    response = HttpResponse('set_cookie')
    # key value
    # max_age 是以秒为单位
    response.set_cookie('name',username,max_age=60*60)
    response.set_cookie('pwd',password)

    # response.delete_cookie('name')

    return response

def get_cookie(request):

    print(request.COOKIES)  # {'name': 'None'}
    name = request.COOKIES.get('name')
    return HttpResponse(name)

"""
Session
    1.session保存在服务器端
    2.session需要依赖于cookie
http://127.0.0.1:8000/set_cookie/username=lishao&password=1024
    第一次请求：在服务器端设置session信息，服务器同时会生成一个sessionid的cookie信息。
浏览器接收到这个信息后，会把cookie信息保存下来。
    第二次及以后请求：都被携带这个sessionid。服务器会验证这个sessionid，
没有问题则读取相关数据，实现业务逻辑。
"""

def set_session(request):

    # 1.模拟获取用户信息
    username = request.GET.get('username')

    # 2.设置session信息
    user_id = 1
    request.session['user_id'] = user_id
    request.session['username'] = username

    # clear 删除session数据，key有保留
    # request.session.clear()
    # flush 删除所有数据，包括key
    # request.session.flush()
    request.session.set_expiry(60*60)
    return HttpResponse('set_session')

def get_session(request):

    # user_id = request.session['user_id']
    # username = request.session['username']

    user_id = request.session.get('user_id')
    username = request.session.get('username')  # 获取字典尽量用.get() 健壮性

    content = f'{user_id},{username}'
    return HttpResponse(content)

"""
类与中间件
    类视图
        定义：
        class 类视图名字（View）:
            
            def get(self,request)
            
                return HttpResponse('xxx')
            
            def http_method_lower(self,request):
            
                return HttpResponse('xxx')
    1.继承自View
"""
def login(request):

    print(request.method)

    if request.method == 'GET':

        return HttpResponse('get逻辑')
    else:
        return HttpResponse('post逻辑')

"""
类视图
        定义：
        class 类视图名字（View）:
            
            def get(self,request)
            
                return HttpResponse('xxx')
            
            def http_method_lower(self,request):
            
                return HttpResponse('xxx')
    1.继承自View
    2.类视图中的方法是采用http方法来区分不同的请求方式
"""
from django.views import View

class LoginView(View):

    def get(self,request):

        return HttpResponse('get get get')

    def post(self,request):

        return HttpResponse('post post post')

# ---------------类视图的多继承重写dispatch-------------
from django.contrib.auth.mixins import LoginRequiredMixin

# class OrderView(LoginRequiredMixin,View):
class OrderView(LoginRequiredMixin,View):

    def get(self,request):
        # 模拟个标记位
        # isLogin = False
        # if not isLogin:
        #     return HttpResponse('你没有登录，跳转到登录界面中~~~~~~')

        return HttpResponse('GET 我的订单界面，页面必须登录！')

    def post(self,request):

        return HttpResponse('POST 我的订单界面，页面必须登录！')

"""
多继承
    python/c++
单继承    
    java/php

"""