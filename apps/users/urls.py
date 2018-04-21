from django.conf.urls import url

from apps.users import views

urlpatterns = [
    # url(r'^register$',views.register,name='register'),
    # url(r'^do_register$',views.do_register,name='do_register'),

    #类视图
    url(r'^register$',views.RegisterView.as_view(),name='register')
]