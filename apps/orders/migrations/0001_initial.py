# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20180420_1117'),
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('count', models.IntegerField(verbose_name='购买数量', default=1)),
                ('price', models.DecimalField(verbose_name='单价', decimal_places=2, max_digits=10)),
                ('comment', models.TextField(verbose_name='评价信息', default='')),
            ],
            options={
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('order_id', models.CharField(verbose_name='订单号', max_length=64, serialize=False, primary_key=True)),
                ('total_count', models.IntegerField(verbose_name='商品总数', default=1)),
                ('total_amount', models.DecimalField(verbose_name='商品总金额', decimal_places=2, max_digits=10)),
                ('trans_cost', models.DecimalField(verbose_name='运费', decimal_places=2, max_digits=10)),
                ('pay_method', models.SmallIntegerField(verbose_name='支付方式', default=1, choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')])),
                ('status', models.SmallIntegerField(verbose_name='订单状态', default=1, choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')])),
                ('trade_no', models.CharField(verbose_name='支付编号', max_length=100, unique=True, default='', blank=True, null=True)),
                ('address', models.ForeignKey(verbose_name='收货地址', to='users.Address')),
                ('user', models.ForeignKey(verbose_name='下单用户', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'df_order_info',
            },
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(verbose_name='所属订单', to='orders.OrderInfo'),
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='sku',
            field=models.ForeignKey(verbose_name='订单商品', to='goods.GoodsSKU'),
        ),
    ]
