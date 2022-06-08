"""
生产者&消费者设计模式
生产者
    @app.task()
    def celery_send_sms_code(mobile,code):

        CCP().send_template_sms(mobile,[code,5],1)

    app.autodiscover_tasks(['celery_tasks.sms'])
消费者
    celery -A proj worker -l INFO

消息中间件/消息队列
celery将3者实现
"""
# 0.为celery运行，设置django环境
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

# 1.创建celery实例
# 参数1：main 设置脚本路径（唯一）
app = Celery('celery_tasks')

# 2.设置broker(通过加载配置文件)
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('celery_tasks.config')

# 3.需要celery自动检测指定包的任务
# Load task modules from all registered Django apps.
# 函数中的参数是列表，列表中的元素是tasks路径
app.autodiscover_tasks(['celery_tasks.sms'])