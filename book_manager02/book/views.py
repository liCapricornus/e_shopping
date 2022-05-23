from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from book.models import BookInfo

# 定义视图函数
def index(request):

    # 在此实现CRUD
    books = BookInfo.objects.all()
    print(books)

    return HttpResponse('index')

"""
    CRUD大法好！
        增加(Create)、检索(Retrieve)、更新(Update)和删除(Delete)
"""
# 增加---Create
from book.models import BookInfo
# 方式1
book = BookInfo(
    name='Django',
    pub_date='2005-7-1',
    readcount=10
)

book.save()

# 方式2 objects---相当于代理，实现CRUD---直接入库
BookInfo.objects.create(
    name='冯诺依曼',
    pub_date='1946-1-1',
    readcount=99
)

# 改---更新Update
# 方式1
# 想当于 select * from bookinfo where id = 8
BookInfo.objects.get(id=8)

book.name = '运维开发入门'

book.save()

# 方式2
BookInfo.objects.filter(id=8).update(name='以AI',commentcount=666)

# BookInfo.objects.get(id=5).update(name='1024',commentcount=555)  # get没有update方法

# 删---Delete
# 方式1
BookInfo.objects.get(id=4)
# 1.物理删除  2.逻辑删除
book.delete()

# 方式2
BookInfo.objects.get(id=2).delete()
BookInfo.objects.filter(id=2).delete()

# 查---Retrieve
"""
查---Retrieve
    get查询单一结果，如果不存在会抛出模型类.DoesNotExist异常。
    
    all查询多个结果。
    
    count查询结果数量。
"""
# 1.get查询单一结果，如果不存在会抛出模型类.DoesNotExist异常。
try:
    book=BookInfo.objects.get(id=1)
except BookInfo.DoesNotExist:
    print("查询结果不存在！")

BookInfo.objects.all()

from book.models import PeopleInfo
PeopleInfo.objects.all()

# count查询结果数量
BookInfo.objects.all().count()  # 等价BookInfo.objects.count()

"""
过滤查询
    实现SQL中的where功能，包括：
        1.filter过滤出多个结果
        2.exclude排除掉符合条件剩下的结果
        3.get过滤单一结果
    对于过滤条件的使用，上述三个方法相同，故仅以filter进行讲解
"""
# 1.filter过滤出多个结果
# 模型类名.objects.filter(属性名__预算符=值)   获取n个结果 n=0,1,2...
# 模型类名.objects.exclude(属性名__预算符=值)  获取n个结果 n=0,1,2...
# 模型类名.objects.get(属性名__预算符=值)      获取1个结果 或者 异常

"""
查询编号为1的图书
查询书名包含'湖'的图书
查询书名以'部'结尾的图书
查询书名为空的图书
查询编号为1或3或5的图书
查询编号大于3的图书
查询1980年发表的图书
查询1990年1月1日后发表的图书
"""
# 查询编号为1的图书
book=BookInfo.objects.get(id=1)

BookInfo.objects.get(pk=1)  # 方式2

BookInfo.objects.get(id=1)
BookInfo.objects.filter(id=1)

# 查询书名包含'湖'的图书
BookInfo.objects.filter(name__contains='湖')

# 查询书名以'部'结尾的图书
BookInfo.objects.filter(name__endswith='部')
BookInfo.objects.filter(name__endswith='传')

# 查询书名为空的图书
BookInfo.objects.filter(name__isnull=True)

# 查询编号为1或3或5的people
PeopleInfo.objects.filter(id__in=[1, 3, 5])
PeopleInfo.objects.filter(id__in=(1, 3, 5))

# 查询编号大于3的图书
# 大于 gt greater than
# 大于等于 gte  equal
# 小于 lt less than
# 小于等于 lte less than equal
BookInfo.objects.filter(id__gt=3)  # 大于3

# 查询编号不等于3的图书
BookInfo.objects.exclude(id=3)

from django.db.models import Q
BookInfo.objects.filter(~Q(id=3))

# 查询1980年发表的图书
BookInfo.objects.filter(pub_date__year=1980)

# 查询1946年1月1日后发表的图书
BookInfo.objects.filter(pub_date__gte='1946-1-1')

"""
F和Q对象
    之前的查询都是对象的属性与常量值比较，两个属性怎么比较呢？
    答：使用F对象，被定义在django.db.models中
"""
from django.db.models import F

# 使用：2个属性的比较
# 语法：以filter为例模型类名.objects.filter(属性名__预算符=F('第二个属性名'))

# 查询阅读量大于等于评论量的图书。
# >>> from django.db.models import F
# >>> BookInfo.objects.filter(readcount__gt=F('commentcount'))
BookInfo.objects.filter(readcount__gte=F('commentcount'))

# 查询阅读量大于2倍评论量的图书
BookInfo.objects.filter(readcount__gt=F('commentcount')*2)

# Q对象
# 多个过滤器逐个调用表示逻辑与关系，同sql语句中where部分的and关键字

# 查询阅读量大于10，并且编号小于等于3的图书
BookInfo.objects.filter(readcount__gt=10).filter(id__lte=3)

BookInfo.objects.filter(readcount__gt=10, id__lt=3)  # 并且

# 如果需要实现逻辑或or的查询，需要使用Q()对象结合|运算符，Q对象被义在django.db.models中

from django.db.models import Q

BookInfo.objects.filter(Q(readcount__gt=20)|Q(id=3))  # 或者

# 非  ~Q
# 查询编号不等于3的图书
BookInfo.objects.exclude(id=3)

BookInfo.objects.filter(~Q(id=3))

"""
聚合函数和排序函数
    使用aggregate()过滤器调用聚合函数。聚合函数包括：
    Avg平均，Count数量，Max最大，Min最小，Sum求和，被定义在django.db.models中。
"""
from django.db.models import Sum,Max,Min,Avg,Count

BookInfo.objects.aggregate(Sum('readcount'))

BookInfo.objects.aggregate(Sum('id'))

# 使用order_by对结果进行排序---排序(升序)
BookInfo.objects.all().order_by('readcount')   # 升序

BookInfo.objects.all().order_by('-readcount')  # 降序

"""
 * 级联操作
"""
from book.models import PeopleInfo
# 查询书籍为1的所有人物信息 --- 1到多
book = BookInfo.objects.get(id=1)

book.peopleinfo_set.all()

# 查询人物为1的书籍信息
person = PeopleInfo.objects.get(id=1)

person.book.name
person.book.readcount

# 关联过滤查询  关联模型类名小写__属性名__条件运算符=值
# 查询图书，要求图书人物为"郭靖"
book = BookInfo.objects.filter(peopleinfo__name__exact='郭靖')
BookInfo.objects.filter(peopleinfo__name='郭靖')

# 查询图书，要求图书中人物的描述包含"八"
BookInfo.objects.filter(peopleinfo__description__contains='八')

# 查询书名为‘天龙八部’的所有人物
PeopleInfo.objects.filter(book__name='天龙八部')

PeopleInfo.objects.filter(book__name='雪山飞狐')

PeopleInfo.objects.filter(book__name='射雕英雄传')

# 查询图书阅读量大于30的所有人物
PeopleInfo.objects.filter(book__readcount__gt=30)

PeopleInfo.objects.filter(book__readcount__lte=20)

"""
Django的ORM中存在查询集的概念。
查询集，也称查询结果集、QuerySet，表示从数据库中获取的对象集合。
    当调用如下过滤器方法时，Django会返回查询集（而不是简单的列表）：
        all()：返回所有数据。
        filter()：返回满足条件的数据。
        exclude()：返回满足条件之外的数据。
        order_by()：对结果进行排序。
两大特性：
    1）惰性执行
        创建查询集不会访问数据库，直到调用数据时，才会访问数据库，调用数据的情况包括迭代、序列化、与if合用
    2）缓存
        使用同一个查询集，第一次使用时会发生数据库的查询，然后Django会把结果缓存下来，
        再次使用这个查询集时会使用缓存的数据，减少了数据库的查询次数。
"""
BookInfo.objects.all()