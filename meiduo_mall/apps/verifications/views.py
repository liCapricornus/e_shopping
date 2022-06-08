import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View


"""
图片验证码 ---------思路---------------------------
前端
    拼接一个url，然后给img，img会发起请求
    url=http://ip:port/image_codes/uuid/

后端
    请求       接收路由中的uuid
    业务逻辑    生成图片验证码和图片二进制，通过redis把图片验证码保存起来
    响应      返回图片二进制
    路由      GET     image_codes/uuid/
    步骤
        1.接收路由中的uuid
        2.生成图片验证码和图片二进制
        3.通过redis把图片验证码保存起来
        4.返回图片二进制
"""
# Create your views here.

class ImageCodeView(View):

    def get(self,request,uuid):
        # 1.接收路由中的uuid
        # 2.生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        text,image = captcha.generate_captcha()
        # 3.通过redis把图片验证码保存起来
        #   3.1 进行redis连接  默认连接的是default get_redis_connection会读取设置中的内容
        from django_redis import get_redis_connection
        redis_cli =  get_redis_connection('code')
        #   3.2 进行指令的连接
        redis_cli.setex(uuid,100,text)

        # 4.返回图片二进制
        return HttpResponse(image,content_type='image/jpeg')  # content_type的语法形式是： 大类/小类
        # 图片：image/jpeg, image/gif, image/png


"""
发送短信的思路
前端：
   当用户输入完手机号，图片验证码之后，前端发送一个axios/ajax请求
   sms_codes/手机号/?image_code= &image_code_id= 
后段：
    请求：接收请求，获取请求参数（路由有手机号，用户的图片验证码和UUID在查询字符串中）
    业务逻辑：验证参数，验证图片验证码，生成短信验证码，保存短信验证码，发送短信验证码
    响应：返回响应
        {'code': 0, 'errmsg': 'ok}
    路由： GET     sms_codes/手机号/?image_code=图形验证码&image_code_id=图形验证码id
    步骤：
        1.获取请求参数
        2.验证参数
        3.验证图片验证码
        4.生成短信验证码
        5.保存短信验证码
        6.发送短信验证码
        7.返回响应
    需求--->思路--->步骤--->代码
    -----------------------------------------------
    debug模式运行，调试模式
    debug和断电配合使用
    可以看到程序执行的过程

    添加断点：在函数体第一行添加断点！！！！ 只有发送请求的时候才会过来

"""

# 短信验证码
class SmsCodeView(View):

    def get(self,request,mobile):
        # 1.获取请求参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2.验证参数
        if not all([image_code,uuid]):
            return JsonResponse({'code':400,'errmsg':'参数不全！'})
        # 3.验证图片验证码
        # 3.1 连接redis
        from django_redis import get_redis_connection

        redis_cli = get_redis_connection('code')
        # 3.2 获取redis数据---拿取数据库中的uuid
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code':400,'errmsg':'图片验证码已过期！'})
        # 3.3 对比
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code':400,'errmsg':'图片验证码错误！'})
        # 3.4提取发送短信的标记，看看有没有
        send_flag = redis_cli.get('send_flag_%s'%mobile)
        if send_flag is not None:
            return JsonResponse({'code':400,'errmsg':'请不要频繁发送短信！'})

        # 4.生成短信验证码
        from random import randint
        sms_code = '%06d'%randint(0,999999)

        # pipeline 3步走  加快性能
        # 1.新建一个管道
        pipeline = redis_cli.pipeline()
        # 2.管道收集指令
        pipeline.setex(mobile,300,sms_code)
        pipeline.setex('send_flag_%s'%mobile,60,1)
        # 3.管道执行指令
        pipeline.execute()

        # 5.保存短信验证码
        # redis_cli.setex(mobile,300,sms_code)
        # # 添加一个发送标记
        # redis_cli.setex('send_flag_%s'%mobile,60,1)

        # 6.发送短信验证码
        from libs.yuntongxun.sms import CCP

        CCP().send_template_sms(mobile,[sms_code,5],1)

        # 7.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!'})






