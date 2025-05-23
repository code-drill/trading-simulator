from django.contrib import admin
from django.contrib.auth.models import User, Group

from rules.models import Market, SaleDefinition

# Register your models here.

admin.site.register(Market)
admin.site.register(SaleDefinition)
admin.site.unregister(User)
admin.site.unregister(Group)