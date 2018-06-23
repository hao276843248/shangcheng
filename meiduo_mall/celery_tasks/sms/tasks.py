from celery_tasks.sms.yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import celery_app


# 使用task装饰器装饰send_sms_code,并起别名
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """异步发送短信任务"""

    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)