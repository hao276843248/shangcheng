from django.http import HttpResponse
from django.shortcuts import render
import random

from celery_tasks.sms.tasks import send_sms_code
from . import serializers
from meiduo_mall.libs.yuntongxun.sms import CCP
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from . import constants
from meiduo_mall.libs.captcha.captcha import captcha
from rest_framework.generics import GenericAPIView


class ImageCodeView(APIView):
    '''生成图片验证码'''

    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    '''发送短信验证码'''
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 忽略校验
        print(11111)
        serializer = self.get_serializer(data=request.query_params)

        # 开启校验
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 存短信验证码到redis数据库
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 创建管道
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 发送短信验证码
        send_sms_code.delay(mobile, sms_code)
        # send_sms_code(mobile, sms_code)
        # CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES//60],constants.SEND_SMS_TEMPLATE_ID)
        print(sms_code)
        # 相应结果

        return Response({'message': 'ok'})


