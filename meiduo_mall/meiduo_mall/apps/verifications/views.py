from django.http import HttpResponse
from django.shortcuts import render
import random

from apps.verifications import serializers
from libs.yuntongxun.sms import CCP
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.verifications import constants
from libs.captcha.captcha import captcha
from rest_framework.generics import GenericAPIView

class ImageCodeView(APIView):

    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type='image/jpg')

class SMSCodeView(GenericAPIView):
    '''发送短信验证码'''
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self,request,mobile):
        # 忽略校验

        serializer = self.get_serializer(data=request.query_params)

        # 开启校验
        serializer.is_valid(raise_exceptio=True)


        # 生成短信验证码
        sms_code='%06d' % random.randint(0,999999)

        # 存短信验证码到redis数据库
        redis_conn=get_redis_connection('verify_code')
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES,sms_code)

        # 发送短信验证码
        print(sms_code)
        # CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES//60],constants.SEND_SMS_TEMPLATE_ID)

        # 相应结果

        return Response({'message':'ok'})
