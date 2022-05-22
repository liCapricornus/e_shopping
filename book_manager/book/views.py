from django.shortcuts import render

# Create your views here.
"""
视图就是一个Python函数，被定义在应用的views.py中.
    1.视图的第一个参数是HttpRequest类型的对象reqeust，包含了所有请求信息.
    2.视图必须返回HttpResponse对象，包含返回给请求者的响应信息.
    3.需要导入HttpResponse模块 :from django.http import HttpResponse
"""
from django.http import HttpRequest
from django.http import HttpResponse

# 用户输入index访问视图函数
def index(request):
    # return HttpResponse('1024摩羯座的胜利')
    # request, template_name, context=None

    # 模拟数据查询
    context01 = {
        'name':'给文明以岁月，给时代以AI.'
    }
    return render(request,'book/index.html',context=context01)