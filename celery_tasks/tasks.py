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
from time import sleep

from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

# 创建celery应用对象
# 参数1： 一个自定义的名字
# 参数2： 使用Redis作为中间人
from django.template import loader

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods

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


@app.task
def generate_static_index_page():
    '''生产静态首页'''
    # sleep(2)
    #查询首页商品数据：商品类别 ，轮播图，促销活动
    categories = GoodsCategory.objects.all()
    slide_skus = IndexSlideGoods.objects.all().order_by('index')
    promotions = IndexPromotion.objects.all().order_by('index')[0:2]

    #定义模板显示的数据

    for c in  categories:
        #display_type=0表示文字，1表示图片
        text_skus = IndexCategoryGoods.objects.filter(display_type=0,category=c)
        image_skus = IndexCategoryGoods.objects.filter(display_type=1,category=c)[0:4]

        #动态给对象增加实例属性
        c.text_skus =text_skus
        c.image_skus = image_skus

    cart_count = 0

    context = {
        'categories': categories,
        'slide_skus': slide_skus,
        'promotions': promotions,
        'cart_count':cart_count,
    }

    #渲染生成静态首页：index.html
    template = loader.get_template('index.html')
    html_str = template.render(context)
    #生成首页
    path = '/home/python/Desktop/static/index.html'
    with open(path,'w') as file:
        file.write(html_str)

