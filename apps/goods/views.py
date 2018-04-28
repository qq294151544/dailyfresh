from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.


# def index(request):
#     return  HttpResponse('首页')
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods, GoodsSKU


class BaseCartView(View):
    # todo:读取用户添加到购物车商品的数量
    def get_cart_count(self, request):
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
    # django 会自动查询登陆的对象，在模板中显示即可
    def get(self, request):
        # 读取redis中的缓存数据
        # 读取缓存:  键=值
        # index_page_data=context字典数据
        context = cache.get('index_page_data')  # 导包导core cache.cache
        # 判断是否有缓存
        if not context:
            print('没有缓存，从mysql数据库中读取')
            # 查询首页商品数据：商品类别 ，轮播图，促销活动
            categories = GoodsCategory.objects.all()
            slide_skus = IndexSlideGoods.objects.all().order_by('index')
            promotions = IndexPromotion.objects.all().order_by('index')[0:2]

            # 定义模板显示的数据

            for c in categories:
                # display_type=0表示文字，1表示图片
                text_skus = IndexCategoryGoods.objects.filter(display_type=0, category=c)
                image_skus = IndexCategoryGoods.objects.filter(display_type=1, category=c)[0:4]

                # 动态给对象增加实例属性
                c.text_skus = text_skus
                c.image_skus = image_skus
            # 定义要缓存的数据
            context = {
                'categories': categories,
                'slide_skus': slide_skus,
                'promotions': promotions,
            }
            # 缓存数据：保存数据到redis中
            # 参数：1：键名，2：数据（字典），3：缓存时间
            cache.set('index_page_data', context, 60 * 30)
        else:
            print('使用缓存')

        cart_count = self.get_cart_count(request)

        context['cart_count'] = cart_count

        # 响应
        return render(request, 'index.html', context)


class DetailView(BaseCartView):
    def get(self, request, sku_id):
        # 查询商品SKU信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            # 没查询到商品就跳转到首页
            return redirect(reverse('gooods:index'))
        # 查询所有商品分类信息
        categories = GoodsCategory.objects.all()
        # 查询最新商品推荐
        try:
            new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]
        except:
            new_skus = None
        # 如果已登录，查询购物车信息
        cart_count = self.get_cart_count(request)
        # todo:查询其他规格商品
        other_skus = GoodsSKU.objects.filter(spu=sku.spu).exclude(id=sku_id)

        # todo:保存用户浏览记录
        if request.user.is_authenticated():
            strict_redis = get_redis_connection()
            key = 'history_%s' % request.user.id
            # 删除list中已存在的id
            strict_redis.lrem(key, 0, sku_id)
            # 再添加商品id到list左侧
            strict_redis.lpush(key, sku_id)
            # 控制元素个数，最多保存五个
            strict_redis.ltrim(key, 0, 4)

        context = {
            'categories': categories,
            'sku': sku,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'other_skus': other_skus,
        }
        return render(request, 'detail.html', context)


class ListView(BaseCartView):
    def get(self, request, category_id, page_num):
        """
        显示商品列表界面
        :param request:
        :param category_id: 类别id
        :param page_num: 页码
        :return:
        """
        # 获取请求参数
        sort = request.GET.get('sort')
        # 校验合法性
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 业务查询
        categories = GoodsCategory.objects.all()  # 商品分类信息
        try:
            new_skus = GoodsSKU.objects.filter(category=category).order_by('-create_time')[0:2]  # 新品分类信息
        except:
            new_skus = None

        # 商品列表信息
        if sort == 'price':
            skus = GoodsSKU.objects.filter(category=category).order_by('price')  # 价格排序

        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')  # 销量排序

        else:
            skus = GoodsSKU.objects.filter(category=category)  # 默认排序
            sort == 'default'
        # 分页
        page_num = int(page_num)
        # 创建分页，每页两条记录
        paginator = Paginator(skus, 4)
        try:
            # 获取分页数据
            page = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，就默认显示第一页数据
            page = paginator.page(1)
        #获取页数列表
        page_list = paginator.page_range

        # 购物车信息
        cart_count = self.get_cart_count(request)
        context = {
            'category': category,  # 当前类别
            'categories': categories,  # 所有类别
            # 'skus': skus,  # 类别下所有的商品
            'new_skus': new_skus,  # 新品推荐
            'cart_count': cart_count,  # 购物车条数
            'sort': sort,  # 排序条件
            'page':page,
            'page_list':page_list,

        }
        return render(request, 'list.html', context)
