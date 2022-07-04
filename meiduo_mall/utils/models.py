from django.db import models

class BaseModel(models.Model):

    """为模型补充字段"""
    # DateField()/年月日  DateTimeField()/年月日+时分秒  DurationField()/一段时间
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")

    class Meta:
        # 说明是抽象模型类，用于继承使用，数据库迁移时不会创建BaseModel的表
        abstract = True