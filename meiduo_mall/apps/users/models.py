from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# 1.自己定义模型
# class User(models.Model):
#     username = models.CharField(max_length=10,unique=True)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=11,unique=True)

# 2. Django 自带用户模型---有密码加密和密码的验证
# from django.contrib.auth.models import User

class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True)

    class Meta:
        db_table='tb_users'   # 指定表明
        verbose_name='用户管理'
        verbose_name_plural=verbose_name
