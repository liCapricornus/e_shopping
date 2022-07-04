from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsCategory, SKU
from utils.goods import get_categories

"""
关于模型的分析
1.根据页面效果 尽量多的分析字段
2.去分析是保存在一个表中 还是多个表中（多举例说明）
分析表的关系的时候 最多不要超过3个表

多对多（一般是3个表）

学生和老师（多对多）
学生表
stu_id          stu_name
100             张三
200             李四

老师表
teacher_id      teacher_name
666             牛老师
999             齐老师

第三张表
stu_id          teacher_id
100             666
100             999
200             666
200             999

商品day01：
    商品模型的分析--->Fdfs（用于保存图片，视频等文件）--->为了部署Fdfs学习Docker

"""

# from fdfs_client.client import Fdfs_client  # 没有下载老师给的 pip install fdfs_client-py-master.zip
# # 1.创建客户端                                 而是下载的 pip install py3Fdfs
# # client = Fdfs_client()
# client = Fdfs_client('utils/fastdfs/client.conf')
# # 2.上传图片
# # client.append_by_filename('/home/lishao/图片/CMU.png')   # 图片绝对路径
# client.upload_by_filename('/home/lishao/图片/CMU.png')
# 3.获取file_id


class IndexView(View):

    def get(self,request):

        """
        首页的数据分为2部分
        1部分是 商品分类数据
        2部分是 广告数据

        """
        # 1.商品分类数据
        categories=get_categories()
        # 2.广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 我们的首页 后边会讲解页面静态化
        # 我们把数据 传递 给 模板
        context = {
            'categories': categories,
            'contents': contents,
        }
        # 模板使用比较少，以后大家到公司 自然就会了
        return render(request,'index.html',context)

"""
需求：
        根据点击的分类，来获取分类数据（有排序，有分页）
前端：
        前端会发送一个axios请求， 分类id 在路由中， 
        分页的页码（第几页数据），每页多少条数据，排序也会传递过来
后端：
    请求          接收参数
    业务逻辑       根据需求查询数据，将对象数据转换为字典数据
    响应          JSON

    路由      GET     /list/category_id/skus/
    步骤
        1.接收参数
        2.获取分类id
        3.根据分类id进行分类数据的查询验证
        4.获取面包屑数据
        5.查询分类对应的sku数据，然后排序，然后分页
        6.返回响应
"""
from django.http import JsonResponse
from utils.goods import get_breadcrumb

class ListView(View):

    def get(self,request,category_id):
        # 1.接收参数
        # 排序字段
        ordering = request.GET.get('ordering')
        # 每页多少条数据
        page_size = request.GET.get('page_size')
        # 第几页
        page = request.GET.get('page')

        # 2.获取分类id
        # 3.根据分类id进行分类数据的查询验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失！'})

        # 4.获取面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 5.查询分类对应的sku数据，然后排序，然后分页
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        # 分页
        from django.core.paginator import Paginator
        # object_list, per_page
        paginator = Paginator(object_list=skus,per_page=page_size)
        # 获取指定页码的数据
        page_skus = paginator.page(page)

        # 将对象转换为dict数据
        sku_list = []
        for sku in page_skus.object_list:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
        # 获取总页数
        total_num = paginator.num_pages

        # 6.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','list':sku_list,'count':total_num,'breadcrumb':breadcrumb})

class HotGoodsView(View):
    """商品热销排行"""
    def get(self,request,category_id):
        # 根据销量降序排列
        skus = SKU.objects.filter(category=category_id,is_launched=True).order_by('-sales')[:2]

        # 序列化
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        # 返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','hot_skus':hot_skus})

"""
 我们/数据         <----------Haystack--------->             elasticsearch 

 我们是借助于 haystack 来对接 elasticsearch
 所以 haystack 可以帮助我们 查询数据
"""
from haystack.views import SearchView
from django.http import JsonResponse


class SKUSearchView(SearchView):

    def create_response(self):
        # 获取搜索的结果
        context = self.get_context()
        # 我们该如何知道里边有什么数据呢？？？
        # 添加断点来分析
        sku_list=[]
        for sku in context['page'].object_list:
            sku_list.append({
                'id':sku.object.id,
                'name':sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })

        return JsonResponse(sku_list,safe=False)


"""
需求：
    详情页面

    1.分类数据
    2.面包屑
    3.SKU信息
    4.规格信息


    我们的详情页面也是需要==静态化==实现的。
    但是我们再讲解静态化之前，应该可以先把 详情页面的数据展示出来

"""

from utils.goods import get_categories
from utils.goods import get_breadcrumb
from utils.goods import get_goods_specs
class DetailView(View):

    def get(self,request,sku_id):
        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
        # 1.分类数据
        categories=get_categories()
        # 2.面包屑
        breadcrumb=get_breadcrumb(sku.category)
        # 3.SKU信息
        # 4.规格信息
        goods_specs=get_goods_specs(sku)

        context = {

            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,

        }
        return render(request,'detail.html',context)


"""
需求：
    统计每一天的分类商品访问量

前端：
    当访问具体页面的时候，会发送一个axios请求。携带分类id
后端：
    请求：         接收请求，获取参数
    业务逻辑：       查询有没有，有的话更新数据，没有新建数据
    响应：         返回JSON

    路由：     POST    detail/visit/<category_id>/
    步骤：

        1.接收分类id
        2.验证参数（验证分类id）
        3.查询当天 这个分类的记录有没有
        4. 没有新建数据
        5. 有的话更新数据
        6. 返回响应
"""

from apps.goods.models import GoodsVisitCount
from datetime import date

class CategoryVisitCountView(View):

    def post(self,request,category_id):
        # 1.接收分类id
        # 2.验证参数（验证分类id）
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此分类'})
        # 3.查询当天 这个分类的记录有没有

        today=date.today()
        try:
            gvc=GoodsVisitCount.objects.get(category=category,date=today)
        except GoodsVisitCount.DoesNotExist:
            # 4. 没有新建数据
            GoodsVisitCount.objects.create(category=category,
                                           date=today,
                                           count=1)
        else:
            # 5. 有的话更新数据
            gvc.count+=1
            gvc.save()
        # 6. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})