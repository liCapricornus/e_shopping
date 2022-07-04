"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from django.http import HttpResponse

# def log(request):
#
#     import logging
#     # 创建日志记录器
#     logger = logging.getLogger('django')
#     # 输出日志
#     logger.info('测试logging模块info')
#     logger.warning('redis缓存不足！')
#     logger.error('测试logging模块error')
#     logger.debug('-----1024-----')
#
#     return HttpResponse('log~~~~~~')

# -----------------注册转换器----------------------
from utils.converters import UsernameConverter
from django.urls import register_converter

register_converter(UsernameConverter,'username')

urlpatterns = [
    path('admin/', admin.site.urls),
    # 导入users子应用的路由
    path('',include('apps.users.urls')),
    path('',include('apps.verifications.urls')),
    path('',include('apps.oauth.urls')),
    path('',include('apps.areas.urls')),
    path('',include('apps.goods.urls')),
    path('',include('apps.carts.urls')),
    # path('',include('apps.contents.urls')),
]
