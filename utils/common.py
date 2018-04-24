from django.contrib.auth.decorators import login_required
from django.views.generic import View


class LoginRequiredView(View):
    '''登陆检测类视图'''
    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)

        #使用装饰器对函数装饰
        return login_required(view_fun)


class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)

        # 使用装饰器对函数装饰
        return login_required(view_fun)