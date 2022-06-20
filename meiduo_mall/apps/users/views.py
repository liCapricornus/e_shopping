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
from apps.users.models import User, Address
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
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


"""
邮箱验证------------------------------->
我的思路：
    用户POST提交保存后，接收前端用户传入的Email数据，将该Email保存到数据库，并返回响应

需求：1.保存邮箱地址 2.发送一封激活邮件 3.用户激活邮件

前端：
    用户输入邮箱后发送ajax（axios）请求
后端：
当用户输入邮箱，点击保存后，会发送ajax请求
    请求      就收请求，获取数据
    业务逻辑    保存邮箱地址 发送一封激活邮件
    响应  JSON code=0
    路由  PUT---> 用来更新数据       var url = this.host + '/emails/'
    步骤
        1.接收请求
        2.获取数据
        3.保存邮箱地址
        4.发送一封激活邮件
        5.返回响应

需求（实现什么功能）---> 请求 --业务逻辑--->响应 ---> 步骤 ---> 代码实现

"""

class EmailView(LoginRequiredJSONMixin,View):

    def put(self,request):
        # 1.接收请求
        data = json.loads(request.body.decode())

        # 2.获取数据
        email = data.get('email')
        # 验证数据
        if not email:
            return JsonResponse({'code':400,'errmsg':'缺少email参数！'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return JsonResponse({'code':400,'errmsg':'email格式错误！'})

        # 3.保存邮箱地址
        user = request.user
        user.email = email
        user.save()

        # 4.发送一封激活邮件
        from django.core.mail import send_mail
        # send_mail(subject, message, from_email, recipient_list）
        subject = '美多商城激活邮件'
        message = ""
        from_email = '美多商城<lishao_1024@163.com>'
        recipient_list = ['285051863@qq.com',
                          # '549456237@qq.com',
                          # '2743318043@qq.com',
                          'lishao_1024@163.com']
        # 4.1对a标签进行加密处理
        # 因itsdangerous 2.0以上版本不可再用TimedJSONWebSignatureSerializer，加密功能暂时不能实现
        token = request.user.id
        # 4.2组织激活邮件

        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % token

        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城</p>' \
                       '<p>您的邮箱为：%s 点击此处链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a>' % (email, verify_url, verify_url)

        # html_message = "点击按钮进行激活<a href='http://www.4399.com'>学习网站请点击！（doge）</a>"

        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=from_email,
        #     recipient_list=recipient_list,
        #     html_message=html_message,
        # )
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
        )

        # 5.返回响应
        return JsonResponse({'code':0,'errmsg':'Set email is OK!'})

"""
需求（知道我们要干什么？？？）：
前端（用户干了什么，传递了什么参数）：
    用户会点击激活链接，那个激活链接携带了token
后端：
    请求：接收请求，获取参数，验证参数
    业务逻辑：user_id ,根据用户的id查询数据，修改数据
    响应：返回响应JSON
    路由：PUT emails/verification/ 说明token并没有在body里
    步骤：
        1.接收请求
        2.获取参数
        3.验证参数
        4.获取user_id
        5.根据用户id查询数据
        6.修改数据
        7.返回响应JSON
"""

class EmailVerifyView(View):

    def put(self,request):
        # 1.接收请求
        params = request.GET
        # 2.获取参数
        token = params.get('token')  # 此处得到的就是user_id
        # 3.验证参数
        if token is None:
            return JsonResponse({'code':400,'errmsg':'参数缺失！'})
        # 4.获取user_id  token是加密令牌，因没有实现解/加密功能，所以
        user_id = token
        if user_id is None:
            return JsonResponse({'code':400,'errmsg':'参数错误！'})
        # 5.根据用户id查询数据
        user = User.objects.get(id=user_id)
        # 6.修改数据
        user.email_active =True
        user.save()
        # 7.返回响应JSON
        return JsonResponse({'code':0,'errmsg':'Verify email is OK!'})


"""
请求
业务逻辑 （数据库的增删改查）
响应

增：（注册的时候）
    1.接收数据
    2.验证数据
    3.数据入库
    4.返回响应
删：
    1.查询到指定记录
    2.删除数据（物理删除，逻辑删除）
    3.返回响应
改：（个人的邮箱信息）
    1.查询到指定的记录
    2.接收数据
    3.验证数据
    4.数据更新
    5.返回响应
查：（个人中心的数据展示, 省市区）
    1.查询指定的数据
    2.将对象数据转换为字典数据
    3.返回响应
"""

"""
需求：
    新增地址
前端：
    当用户填写完成地址信息后，前端应该发送一个axios请求,会携带相关信息（POST---body)
后端：
    请求：接收请求，获取参数
    业务逻辑：数据入库
    响应：返回响应
    路由：     POST    /addresses/create/
    步骤：
        1.接收请求
        2.获取参数，验证参数
        3.数据入库
        4.返回响应
"""

from apps.areas.models import Area

class AddressCreateView(LoginRequiredJSONMixin,View):

    def post(self,request):
        """实现新增地址逻辑"""
        # 1.接收请求
        data = json.loads(request.body.decode())

        # 2.获取参数，验证参数
        receiver=data.get('receiver')
        province_id=data.get('province_id')
        city_id=data.get('city_id')
        district_id=data.get('district_id')
        place=data.get('place')
        mobile=data.get('mobile')
        tel=data.get('tel')
        email=data.get('email')
        user = request.user
        # 验证参数
        # 2.1 验证必传参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 3.2省市区的id是否正确（如果能在区表中查到市，根据市查到区/县说明id正确）
        province = Area.objects.get(id=province_id)
        city = Area.objects.get(id=city_id)
        district = Area.objects.get(id=district_id)
        if not all([province, city, district]):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的地区信息'})
        # 3.3详细地址的长度
        if len(place) > 50:
            return JsonResponse({'code': 400, 'errmsg': '地址过长'})
        # 3.4手机号
        if not re.match('1[345789]\d{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号不正确，请重新输入'})
        # 3.5固定电话
        if len(tel) > 0:
            if not re.match('(\d{4}-)?\d{6,8}', tel):
                return JsonResponse({'code': 400, 'errmsg': '电话格式不正确'})
        # 3.6邮箱
        if len(email) > 0:
            if not re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email):
                return JsonResponse({'code': 400, 'errmsg': '邮箱格式不正确'})

        # 3.数据入库
        address = Address.objects.create(
            user=user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email,
        )
        # 转换为字典
        address_dict = {
            'user':address.user.username,
            'id':address.id,
            'title':address.title,
            'receiver':address.receiver,
            'province_id':address.province.name,
            'city_id':address.city.name,
            'district_id':address.district.name,
            'place':address.place,
            'mobile':address.mobile,
            'tel':address.tel,
            'email':address.email,
        }

        # 4.返回响应

        return JsonResponse({'code':0,'errmsg':'OK!','address':'address_dict'})

    # 修改地址
    def put(self, request, address_id):

        # 1.接收数据
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')

        # 1.5 查询到的为未改变的数据 需求：拿到用户输入的数据 TODO
        province = data.get('province')
        city = data.get('city')
        district = data.get('district')

        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        # 2. 修改数据
        address = Address.objects.get(id=address_id)
        address.receiver = receiver

        address.province_id = province
        address.city_id = city
        address.district_id = district

        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email

        address.save()
        # 3.封装字典
        address_dict = {
            'receiver': receiver,
            'province': province,
            'city': city,
            'district': district,
            'place': place,
            'mobile': mobile,
            'tel': tel,
            'email': email
        }
        address.save()
        # 4.返回响应
        return JsonResponse({'code': 0, 'message': 'modify address is ok', 'address': address_dict})

    # 删除地址
    def delete(self, request, address_id):
        # 1.获取数据
        # 2.查询数据
        address = Address.objects.get(id=address_id)
        # 3.删除数据
        try:
            address.delete()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': 'delete is ok'})
        # 4.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'delete is ok'})


"""地址展示实现"""
class AddressView(LoginRequiredJSONMixin,View):

    def get(self,request):
        # 1.查询指定数据
        user = request.user
        addresses = Address.objects.filter(user=user.id,is_deleted=False)
        # 2.将对象转换为字典
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email
            })
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','addresses':address_list,'default_adress_id':user.default_address_id})


"""修改标题功能实现"""
class AddressTitleView(LoginRequiredJSONMixin,View):
    # axios.put(this.host + '/addresses/' + this.addresses[index].id + '/title/', {
    def put(self,request,address_id):
        # 1.获取数据
        data = json.loads(request.body.decode())
        title = data.get('title')
        # user = request.user

        # 2.修改指定数据
        address = Address.objects.get(id=address_id)
        address.title = title
        address.save()

        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'修改标题功能实现！'})

"""默认地址功能实现"""
class AddressDefaultView(LoginRequiredJSONMixin,View):


    def put(self,request,address_id):
        # 1.修改数据
        user = request.user
        user.default_address_id = address_id
        user.save()

        # 2.返回响应
        return JsonResponse({'code':0,'errmsg':'默认地址设置完毕！'})

"""修改密码的实现"""
class PasswordChangeView(View):

    def put(self,request):
        # 1.查询信息
        user =request.user
        # 2.接收数据
        data = json.loads(request.body.decode())
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')

        # 3.验证数据
        user = authenticate(username=user.username,password=old_password)
        if not user:
            return JsonResponse({'code':400,'errmsg':'密码输入不正确请重新输入！'})
        if new_password != new_password2:
            return JsonResponse({'code':400,'errmsg':'密码输入不一致！'})

        # 4.数据更新
        user.set_password(new_password)
        user.save()

        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': '成功修改密码！'})

