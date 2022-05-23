from django.db import models

# Create your models here.
"""
1.定义模型类
2.定义属性
    2.1属性名(字段名)=models.类型（选项）
    2.2类型---mysql类型
    2.3选项
3.改变表的名称
"""
class BookInfo(models.Model):

    name = models.CharField(max_length=10, unique=True,verbose_name='名字')  # unique=True---名字唯一
    pub_date = models.DateField(null=True)
    readcount = models.IntegerField(default=0)
    commentcount = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)

    # peopleinfo_set = [PeopleInfo,PeopleInfo...]
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'bookinfo'  # 修改表的名字
        verbose_name = '书籍管理1024'

class PeopleInfo(models.Model):
    # 定义一个有序字典
    GENDER_CHOICE = (
        (1, 'male'),
        (2, 'female'),
    )

    name = models.CharField(max_length=10, unique=True)
    gender = models.SmallIntegerField(choices=GENDER_CHOICE, default=1)
    description = models.CharField(max_length=100, null=True)
    is_delete = models.BooleanField(default=False)

    # 外键
    # 主表和从表
    book = models.ForeignKey(BookInfo,on_delete=models.CASCADE)
    # book = BookInfo()
    class Meta:
        db_table = 'peopleinfo'

    def __str__(self):
        return self.name