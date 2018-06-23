# celery服务器的入口
from celery import Celery


# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 创建celery客户端实例,并起别名
celery_app = Celery('meiduo',broker = "redis://192.168.167.55:6379/12")

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')


# 自动注册异步任务:celery会自动的寻找封装异步任务的包里面的tasks.py文件
# 就是告知celery_app去哪里找异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])
