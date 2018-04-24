from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from apps.users import views

urlpatterns = [
    # url(r'^register$',views.register,name='register'),
    # url(r'^do_register$',views.do_register,name='do_register'),

    #类视图
    url(r'^register$',views.RegisterView.as_view(),name='register'),
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='active'),
    url(r'^login$',views.LoginView.as_view(),name='login'),
    url(r'^logout$',views.LogoutView.as_view(),name='logout'),
    url(r'^orders$',views.UserOrderView.as_view(),name='orders'),
    url(r'^address$',login_required(views.UserAddressView.as_view()),name='address'),
    url(r'^$', views.UserInfoView.as_view(), name='info'),#匹配空字符串放在最后

]