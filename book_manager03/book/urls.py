from django.urls import path
from book.views import create_book, shop, register, json, method, response, set_cookie, get_cookie, login, OrderView
from book.views import set_session,get_session
from book.views import LoginView

from django.urls import converters
from django.urls.converters import register_converter

# 1.定义转换器
class MobileConverter:
    #  验证数据的关键：正则
    regex = '1[3-9]\d{9}'    # '[0-9]+'

    # 验证没有问题的数据给视图函数
    def to_python(self, value):
        return value

    # def to_url(self, value):
    #     return value

# 2.注册转换器--然后再使用
# def register_converter(converter, type_name):
register_converter(MobileConverter,'phone')

urlpatterns = [
    path('create/',create_book),
    # path('11000/11005/', shop),
    # path('11000/11004/', shop),

    # <转换器名字：变量名>
    # 转换器会对变量数据进行 正则的验证

    path('<int:city_id>/<phone:mobile>/', shop),  # 两个占位符
    path('register/', register),
    path('json/', json),
    path('method/', method),
    path('res/', response),
    path('set_cookie/', set_cookie),
    path('get_cookie/', get_cookie),
    path('set_session/', set_session),
    path('get_session/', get_session),
    path('login/',login),
    # ----------类视图-------------
    path('163login/',LoginView.as_view()),

    path('order/',OrderView.as_view()),
]