import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    # write_only : 负责输入，辅助校验
    password2 = serializers.CharField(write_only=True, label='确认密码')
    sms_code = serializers.CharField(write_only=True, label='短信验证码')
    allow = serializers.CharField(write_only=True, label='是否同意相关说明')

    # 补充token字段:read_only负责输出，要响应出去的字段
    token = serializers.CharField(read_only=True,label='登录状态token')


    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile','password2','sms_code','allow','token')
        # 定义扩展  单独校验
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的用户名',
                    'max_length': '仅允许8-20个字符的用户名',
                }
            }
        };

    # 校验手机号是否正确
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    # 校验是否同意协议
    def validate_allow(self, value):
        if value.lower() != "true":
            raise serializers.ValidationError('请同意协议')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')
        redies_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        redis_sms=redies_conn.get('sms_%s' % mobile)
        print(redis_sms,"------")
        print(attrs['sms_code'])
        if redis_sms == None:
            raise serializers.ValidationError('短信验证码无效')
        elif redis_sms.decode() != attrs['sms_code']:
            raise serializers.ValidationError('短信验证码不正确')
        return attrs

    def create(self, validated_data):
        """
        创建用户
        :param validated_data:
        :return:
        """
        # 移除数据库中不存在的字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user=super().create(validated_data)

        # 调用django的认证系统加密 密码
        user.set_password(validated_data['password'])
        user.save()

        # 在响应user前，生成jwt_token
        jwt_payload_handler=api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler=api_settings.JWT_ENCODE_HANDLER

        payload=jwt_payload_handler(user)
        jwt_token=jwt_encode_handler(payload)

        user.token=jwt_token
        return user

