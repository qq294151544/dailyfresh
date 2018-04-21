from django.contrib import admin

# Register your models here.
from apps.users.models import TestModel

admin.site.register(TestModel)