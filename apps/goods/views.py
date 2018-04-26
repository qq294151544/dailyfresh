from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.


# def index(request):
#     return  HttpResponse('首页')
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods

class BaseCartView(View):
    # todo:读取用户添加到购物车商品的数量
    def get_cart_count(self,request):
        cart_count = 0  # 购物车商品总数量
        if request.user.is_authenticated():  # 判断登陆
            strict_redis = get_redis_connection()
            key = 'cart_%s' % request.user.id  # cart_1={1:2,2:2}
            # 返回的是list类型，储存的元素类型 bytes
            vals = strict_redis.hvals(key)
            for count in vals:
                cart_count += int(count)
        return cart_count
class IndexView(BaseCartView):
    #django 会自动查询登陆的对象，在模板中显示即可
    def get(self,request):

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

        cart_count = self.get_cart_count(request)

        context = {
            'categories': categories,
            'slide_skus': slide_skus,
            'promotions': promotions,
            'cart_count':cart_count,
        }

        #响应
        return render(request,'index.html',context)

