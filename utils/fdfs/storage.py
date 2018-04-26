from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    '''自定义储存类，当管理员在管理后台上传文件时，会使用此类保存上传文件'''

    def _save(self, name, content):
        # name:文件名 content:从对象上获取上传的文件内容
        # path = super()._save(name, content)
        # print(name, path, type(content))
        # 上传的文件路径，此路径保存在表中


        # todo:保存文件到fastdfs服务器上
        client = Fdfs_client('utils/fdfs/client.conf')
        try:
            #上传文件到fds服务器
            data = content.read() #要上传的文件内容
            result=client.upload_appender_by_buffer(data)#返回一个json字符串
            status = result.get('Status')
            if status == 'Upload successed.':
                path = result.get('Remote file_id')
            else:
                raise  Exception('图片上传失败：%s' % status)


        except Exception as e:

            print(e)
            raise e
        print(path)
        return path

    def url(self, name):
        #拼接nginx服务器的ip和端口
        path= super().url(name)
        return 'http://127.0.0.1:8888/'+path

