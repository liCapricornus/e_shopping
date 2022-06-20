from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from apps.areas.models import Area

# Create your views here.

"""
需求：
    获取省份信息
前端：
    当页面加载的时候，会发送axios请求来获取省份信息
后端：
    请求：     不需要请求参数
    业务逻辑：   查询省份信息
    响应：     JSON

    路由：     areas/
    步骤：      
            1.查询省份信息
            2.返回响应
"""

"""访问用户中心界面的时候加载 市"""

class AreaView(View):

    def get(self,request):

        # 先查询缓存数据
        province_list = cache.get('province')
        # 如果没有缓存，则查询数据库并缓存数据
        if province_list is None:
            # 1.查询省份信息
            provinces = Area.objects.filter(parent=None)
            # 2.将对象转换为字典数据
            province_list = []
            for province in provinces:
                province_list.append(
                    {'id':province.id,'name':province.name,}
                )
            #  保存缓存数据
            cache.set('province',province_list,24*3600)
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK!','province_list':province_list})

"""
需求：
    获取市，区/县信息
前端：
    当页面加载的时候，会发送axios请求来获取 下一级信息
后端：
    请求：     需要传递省份id，市的id
    业务逻辑：   根据id查询信息，将查询的结果转化为字典列表
    响应：     JSON

    路由：     areas/  GET
    步骤：      
            1.查询省份id，市的id，查询信息
            2.将数据转化为字典数据
            3.返回响应
"""

""" 根据市的id查询下一级的信息"""

class SubAreaView(View):

    def get(self,request,id):

        # 查询缓存信息
        # data_list = cache.get('citys:%s'%id)
        data_list = cache.get(f'citys:{id}')
        # data_list = cache.get(id)
        # 如果没有缓存，则查询数据库并缓存数据
        if data_list is None:
            # 1.查询省份id，市的id，查询信息
            up_level = Area.objects.get(id=id)
            down_level = up_level.subs.all()

            # 2.将数据转化为字典数据
            data_list = []
            for item in down_level:
                data_list.append(
                    {'id':item.id,'name':item.name}
                )
            # 缓存数据
            # cache.set('city:%s'%id,data_list,24*3600)
            cache.set(f'city:{id}',data_list,24*3600)
            # cache.set(id,data_list,24*3600)  # 也可以
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK!','sub_data':{'subs':data_list}})
