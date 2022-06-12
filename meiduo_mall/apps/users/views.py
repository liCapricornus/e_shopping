from django.shortcuts import render

# Create your views here.

"""
需求分析
    根据功能，哪些功能需要和后端配合完成
    从上倒下，从左到右。
如何确定哪些功能需要和后端进行交互？
    1.经验
    2.关注类似网站的相似功能。
"""

"""
功能---判断用户名是否重复
    前端：用户输入用户名后，失去焦点，发送一个axiox/ajax请求
    后端：
        接收请求：接受用户名
        处理业务逻辑：根据用户名，查询数据库，if 查询数量 == 0，则没有注册，else 如果 查询数量 == 1，则已注册
        发出响应：JSON数据 （code:0,count:0/1,errmsg:ok）
    路由：GET
    步骤：
        1.接收用户名
        2.查询---根据用户名查询数据库
        3.返回响应
"""
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
from django.contrib.auth import login, logout
import re
import json


class UsernameCountView(View):

    def get(self,request,username):
        # 1.接收用户名(对用户名进行判断)  JSON数据
        # if not re.match('[a-zA-Z0-9_-]{5,20}',username):
        #     return JsonResponse({'code':200,'errmsg':'用户名不满足要求！'})
        # 2.查询---根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        # 3.返回响应
        return JsonResponse({'code':0,'count':count,'errmsg':'OK'})


"""
用户注册
    前端：用户输入用户名+密码，确认密码+手机号，同意协议后，点击注册
        前端会发送axios请求
        
    后端：
        1.接收请求，获取数据
        2.业务逻辑：验证数据，数据入库
        3.响应：JSON数据 {'code':0,'errmsg':'OK'}
            响应码：0---表示成功 400---表示失败
    
    路由： POST register/
    
    步骤：
        1.接收请求（POST---JOSN）
        2.获取数据
        3.验证数据
            3.1 用户名+密码+确认密码+手机号+同意协议
            3.2 用户名不能重复+满足RE规则
            3.3 密码满足RE规则
            3.4 确认密码和输入密码一致
            3.5 手机号不能重复
            3.6 需要同意协议
        4.数据入库
        5.返回响应
"""

# 判断手机号是否注册
# class PhoneNumberCountView(View):
#     def get(self, request, mobile):
#         # 1.接收手机号
#         # 2.根据电话号查询
#         count = User.objects.filter(mobile=mobile).count()  # 查询手机号对应的数量
#         # 3.返回
#         return JsonResponse({'code': 0, 'count': count, 'errmsg': 'set phone is ok'})

class RegisterView(View):

    def post(self,request):
        # 1.接受数据
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)

        # 2.获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # 3.验证数据
        #   3.1 用户名+密码+确认密码+手机号+同意协议
        # all([xxx,xxx,xxx])中元素null/false就返回false
        if not all([username,password,password2,mobile]):  # if true则 all()中有null/false,则返回错误 400  # 去掉allow
            return JsonResponse({'code':400,'errmsg':'输入参数有误！'})
        #   3.2 用户名不能重复+满足RE规则
        if User.objects.filter(username=username):
            return JsonResponse({'code':400,'errmsg':'用户名已存在！'})
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}',username):
            return JsonResponse({'code':400,'errmsg':'用户名格式有误！'})
        #   3.3 密码满足RE规则
        if not re.match(r'^[a-zA-Z0-9]{8,20}',password):
            return JsonResponse({'code':400,'errmsg':'密码格式有误！'})
        #   3.4 确认密码和输入密码一致
        if password != password2:
            return JsonResponse({'code':400,'errmsg':'密码不一致，请重试！'})
        #   3.5 手机号不能重复
        if not re.match(r'^1[345789]\d{9}',mobile):
            return JsonResponse({'code':400,'errmsg':'手机号不满足格式！'})
        if User.objects.filter(mobile=mobile):
            return JsonResponse({'code':400,'errmsg':'该手机号已注册！'})
        #   3.6 需要同意协议
        # if allow is False:
        #     return JsonResponse({'code':400,'errmsg':'请勾选同意协议！'})

        # 4.数据入库
        # 方案一
        # user = User(username=username, password=password, mobile=mobile)
        # user.save()

        # 方案二  以上2中方式中，都可以入库，但是有一个问题？--->密码没有加密
        # User.objects.create(username=username, password=password, mobile=mobile)

        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 状态保持 设置session信息
        login(request,user)

        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': '注册成功！'})



"""
登录---1.注册成功后，表示用户认证通过，状态保持（注册成功即登录）/2.注册成功，不表示用户认证通过（注册成功后重新登录）

实现状态保持主要有两种方式：
    1.在客户端存储信息使用Cookie
    2.在服务器端存储信息使用Session(相对安全，首选)

验证码
    1.将图形验证码的文字信息保存到Redis数据库，为短信验证码做准备。
    2.UUID 用于唯一区分该图形验证码属于哪个用户，也可使用其他唯一标识信息来实现。
"""
# -----------------------login----------------------------
"""
登录

前端：
    当用户把用户名和密码输入完成之后，会点击登录摁钮。这个时候前端会发送一个ajax（axios）请求

后端：
    请求：接收数据，验证数据
    业务逻辑：验证用户名和密码是否正确，session（状态保持）
    响应：返回json数据 0 成功 400 失败

    POST    /login/

步骤：
    1.接收数据
    2.验证数据
    3.验证用户名和密码是否正确
    4.session
    5.判断是否记住登录
    6.返回响应
"""

class LoginView(View):

    def post(self,request):
        # 1.接收数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 2.验证数据
        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全！'})
        # 2.5.验证是根据手机号查询还是根据用户名查询   可以根据修改User.USERNAME_FIELD字段来确定是用户名/手机号来进行判断是什么登录
        if re.match('1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 3.验证用户名和密码是否正确
        # 方案一（查询数据库）
        # user = User.objects.filter(username=username,password=password)
        # if not user:
        #     return JsonResponse({'code':400,'errmsg':'用户名或者密码错误！'})
        # 方案二（系统提供）
        from django.contrib.auth import authenticate
        # authenticate 传递用户名+密码
        # 如果用户名+密码输入正确，返回User信息
        # 不正确则返回None
        user = authenticate(username=username,password=password)
        if user is None:
            return JsonResponse({'code':400,'errmsg':'用户名或者密码错误！'})

        # 4.session
        login(request,user)

        # 5.判断是否记住登录
        if remembered is True:
            # 记住登录
            request.session.set_expiry(None)
        else:
            # 不记住登录 浏览器关闭session过期
            request.session.set_expiry(0)

        # 6.返回响应
        response = JsonResponse({'code':0,'errmsg':'OK!'})
        response.set_cookie('username',username)
        return response


"""
退出登录----------------------------------------------------------------->
前端：
    当用户点击退出摁钮的时候，前端发送一个axios delete的请求
后段：
    请求
    业务逻辑    退出
    响应 发挥JSON数据

"""

class LogoutView(View):

    def delete(self,request):
        # 1.删除session信息
        logout(request)

        response = JsonResponse({'code':400,'errmsg':'OK!'})
        # 2.删除cookie信息，前端会记录cookie信息+session id
        response.delete_cookie('username')

        return response

"""
用户中心
    LoginRequiredMixin 未登录的用户返回重定向的不是JSON数据
"""
from utils.views import LoginRequiredJSONMixin

class CenterView(LoginRequiredJSONMixin,View):

    def get(self,request):

        info_data = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }

        return JsonResponse({'code':0,'errmsg':'OK!','info_data':info_data})  # if 没有登录就不会返回JSON数据



