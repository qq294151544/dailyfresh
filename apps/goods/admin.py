from django.contrib import admin

# Register your models here.
from django.core.cache import cache

from apps.goods.models import *
from celery_tasks.tasks import *


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''管理后台新增或者修改了模型数据后调用'''
        super().save_model(request,obj,form,change)
        print('save_model: %s' % obj)
        generate_static_index_page.delay()
        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''管理后台删除了一条数据后调用'''
        super().delete_model(request,obj)
        print('delete_model: %s' % obj)
        generate_static_index_page.delay()
        cache.delete('index_page_data')


class GoodsCategoryAdmin(BaseAdmin):
    pass


class GoodsSPUAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


class IndexSlideGoodsAdmin(BaseAdmin):
    pass


class IndexPromotionAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsAdmin(BaseAdmin):
    list_display = ['id']
    pass

admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(GoodsSPU,GoodsSPUAdmin)
admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(IndexSlideGoods,IndexSlideGoodsAdmin)
admin.site.register(IndexPromotion,IndexPromotionAdmin)
admin.site.register(IndexCategoryGoods,IndexCategoryGoodsAdmin)
