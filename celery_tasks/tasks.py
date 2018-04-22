# import os
# import django
#
# from django.core.wsgi import get_wsgi_application
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
#
# application = get_wsgi_application()
#
# django.setup()
# #在selery服务器所在项目中手动初始化django


from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

# 创建celery应用对象
# 参数1： 一个自定义的名字
# 参数2： 使用Redis作为中间人
app = Celery('dailyfresh', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_email(username, receiver, token):
    """发送激活邮件"""
    subject = "天天生鲜用户激活"  # 标题, 不能为空，否则报错
    message = ""  # 邮件正文(纯文本)
    sender = settings.EMAIL_FROM  # 发件人
    receivers = [receiver]  # 接收人, 需要是列表
    # 邮件正文(带html样式)
    html_message = ('<h3>尊敬的%s：感谢注册天天生鲜</h3>'
                    '请点击以下链接激活您的帐号:<br/>'
                    '<a href="http://127.0.0.1:8000/users/active/%s">'
                    'http://127.0.0.1:8000/users/active/%s</a>'
                    ) % (username, token, token)
    send_mail(subject, message, sender, receivers,
              html_message=html_message)
