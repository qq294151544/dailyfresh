import re

from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from apps.users.models import User
from dailyfresh import settings


def register(request):
    return render(request,'register.html')

def do_register(request):

    return  HttpResponse('注册成功，进入登陆界面')

class RegisterView(View):

    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        # 获取post参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 判断参数不能为空
        if not all([username , password, password2, email, allow]):
            return render(request, 'register.html', {'ERRORMSG': '参数不能为空'})
        # 判断输入两次密码一致
        if password != password2:
            return render(request, 'register.html', {'ERRORMSG': '输入两次密码不一致'})

        # 判断邮箱合法性
        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'ERRORMSG': '输入邮箱不合法'})

        # 判断是否勾选用户协议
        if allow != 'on':
            return render(request, 'register.html', {'ERRORMSG': '未勾选用户协议'})

        try:
            # 处理业务：保存用户到数据库表中
            user = User.objects.create_user(username, email, password)
            # 修改用户状态为未激活
            user.is_active = False
            user.save()
            # 判断用户是否存在
        except IntegrityError:
            return render(request, 'register.html', {'ERRORMSG': '用户已存在'})

        # todo:发送激活邮件
        token = user.generate_active_token()
        RegisterView.send_active_email(username,email,token)
        return  HttpResponse('注册成功，进入登陆界面')

    @staticmethod
    def send_active_email(username, receiver, token):
        """发送激活邮件"""
        subject = "天天生鲜用户激活"  # 标题, 不能为空，否则报错
        message = "JOJO我不做人了！"  # 邮件正文(纯文本)
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