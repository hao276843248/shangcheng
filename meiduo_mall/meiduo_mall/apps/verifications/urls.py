from django.conf.urls import url
from . import views


urlpatterns=[
    # 图片验证码
    url('^image_codes/(?P<image_code_id>[\w-]+)/$',views.ImageCodeView.as_view()),
    # 短信验证码
    url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$',views.SMSCodeView.as_view()),
]