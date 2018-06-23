from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

import logging

logger = logging.getLogger('django')



class ImageCodeCheckSerializer(serializers.Serializer):
    '''图片验证码序列化器'''

    # 定义校验的字段：字段名，必须和外界传入参数的一致：url查询参数名一致
    image_code_id=serializers.UUIDField()
    text=serializers.CharField(max_length=4,min_length=4)


    # 校验
    def validate(self, attrs):
        '''对比服务器图片验证码和客户端传入的图片验证码'''

        # 取出经过字段校验后的数据
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 使用image_code_id查询出redis中存储的图片验证码
        redis_conn=get_redis_connection('verify_codes')
        image_code_server=redis_conn.get('img_%s' % image_code_id)
        if image_code_server is None:
            raise serializers.ValidationError('无效图片验证码')

        # 删除验证码：防止暴力测试
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)
        # 对比客户端和服务器的验证码
        # 因为py3中的redis，会将数据以原始形态返回读取者
        # 存储数据都是bytes类型，而读取的时候也保持原始的bytes类型，因为速度快
        image_code_server=image_code_server.decode()
        if text.lower() != image_code_server.lower():
            raise serializers.ValidationError('输入图片验证码有误')

        mobile = self.context['view'].kwargs['mobile']
        send_flag= redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信验证码过于频繁')

        return attrs











