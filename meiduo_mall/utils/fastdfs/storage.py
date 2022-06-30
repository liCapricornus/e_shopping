"""

https://docs.djangoproject.com/en/1.11/howto/custom-file-storage/

1. 您的自定义存储系统必须是的子类 django.core.files.storage.Storage
2. Django必须能够在没有任何参数的情况下实例化您的存储系统
        我们在创建存储类的时候，不传递任何参数
3. 您的存储类必须实现_open()和_save() 方法，以及适用于您的存储类的任何其他方法
    url
"""

from django.core.files.storage import Storage

# 自定义文件存储类 可以访问到渲染的templates 主页
class MyStorage(Storage):
    def open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        pass

    # 这两个方法复制 系统_open中的
    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        pass

    def url(self, name):
        # TODO 修改域名优化访问速度
        return 'http://192.168.1.6:8888/' + name