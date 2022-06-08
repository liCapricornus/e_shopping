from django.urls import converters
class UsernameConverter:   # 转换器先注册再使用
    regex='[a-zA-Z0-9_-]{5,20}'

    def to_python(self,value):
        return value