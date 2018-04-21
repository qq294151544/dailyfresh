import re

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def register(request):
    return render(request,'register.html')

def do_register(request):
    #获取post参数
    username = request.POST.get('username')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    #todo:校验参数合法性

    #判断参数不能为空
    if not all([username,password,password2,email,allow]):
        return render(request,'register.html',{'ERRORMSG':'参数不能为空'})
    #判断输入两次密码一致
    if password != password2:
        return render(request,'register.html',{'ERRORMSG':'输入两次密码不一致'})

    #判断邮箱合法性
    if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        return render(request, 'register.html', {'ERRORMSG': '输入邮箱不合法'})

    #判断是否勾选用户协议
    if allow != 'on':
        return render(request, 'register.html', {'ERRORMSG': '未勾选用户协议'})


    return  HttpResponse('注册成功，进入登陆界面')