import os

try:
    import oss2
except ImportError:
    import subprocess
    subprocess.call(['pip', 'install', 'oss2'])
    import oss2

__all__ = ('put_object',)

access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
bucket_name = os.getenv('OSS_BUCKET_NAME')

if not all((access_key_id, access_key_secret, bucket_name)):
    raise OSError("Environment variable OSS is not set")

endpoint = 'http://oss-cn-hangzhou.aliyuncs.com'  # 以杭州为例
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)


def put_object(key, data):
    """上传一个普通文件。

    用法 ::
            >>> put_object('readme.txt', 'content of readme.txt')
            >>> with open(u'local_file.txt', 'rb') as f:
            >>>     put_object('remote_file.txt', f)

    :param key: 上传到OSS的文件名

    :param data: 待上传的内容。
    :type data: bytes，str或file-like object
    """

    # 将 x-oss-forbid-overwrite 属性设置为 false，以覆盖已经存在的文件
    headers = {
        'x-oss-forbid-overwrite': 'false',
        'Content-Type': 'text/plain'
    }
    bucket.put_object(key, data, headers=headers)


if __name__ == '__main__':
    """ pip install oss2
    
    github actions example
    
    - name: update local file
      env:
       OSS_ACCESS_KEY_ID: ${{secrets.OSS_ACCESS_KEY_ID}}
       OSS_ACCESS_KEY_SECRET: ${{secrets.OSS_ACCESS_KEY_SECRET}}
       OSS_BUCKET_NAME: ${{secrets.OSS_BUCKET_NAME}}
      run: python script.py
    
    """
    put_object("1.txt", "hello")
