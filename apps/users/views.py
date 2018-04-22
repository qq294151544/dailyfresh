import re

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from apps.users.models import User
from celery_tasks.tasks import send_active_email
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
        #同步发送会阻塞
        # RegisterView.send_active_email(username,email,token)

        #异步调用delay方法
        send_active_email.delay(username,email,token)
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


class ActiveView(View):

    def get(self, request, token: str):
        """
        激活注册用户
        :param request:
        :param token: 对{'confirm':用户id}字典进行加密后的结果
        :return:
        """
        # 解密数据，得到字典
        dict_data = None
        try:
            s = TimedJSONWebSignatureSerializer(
                settings.SECRET_KEY, 3600*24)
            dict_data = s.loads(token.encode())     # type: dict
        except SignatureExpired:
            # 激活链接已经过期
            return HttpResponse('激活链接已经过期')

        # 获取用id
        user_id = dict_data.get('confirm')

        # 激活用户，修改表字段is_active=True
        User.objects.filter(id=user_id).update(is_active=True)

        # 响应请求
        return HttpResponse('激活成功，进入登录界面<a style="color: red" href="/index">请点击进入首页</a>')
        # return render(request,'index.html')

class LoginView(View):
    def get(self,request):
        return  render(request,'login.html')


    def post(self,request):
        # return redirect('/index.html')
        #获取请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        #校验合法性
        if not all([username,password]):
            return render(request,'login.html',{'ERRMSG':'用户名与密码不能为空'})
        #业务处理：登陆
        user = authenticate(username=username,password=password)#django自带模块校验用户名和密码
        if user is None:
            return render(request,'login.html',{'ERRMSG':'用户名密码不正确'})
        if not user.is_active:
            return render(request,'login.html',{'ERRMSG':'用户未激活'})
        #登陆成功后，使用session保存用户登陆状态调用的是django的模块进行自动保存
        #request.session['user_id'] = user.id 获取
        login(request,user)
        #响应请求
        return redirect(reverse('goods:index'))

class LogoutView(View):
    def get(self,request):
        #注销用户登陆,直接调用方法实现退出，并会清除session数据
        logout(request)
        return redirect(reverse('goods:index'))