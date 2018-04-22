from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.


# def index(request):
#     return  HttpResponse('首页')
from django.views.generic import View


class IndexView(View):
    #django 会自动查询登陆的对象，在模板中显示即可
    def get(self,request):
        return render(request,'index.html')

