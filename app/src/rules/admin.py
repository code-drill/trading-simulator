from django.contrib import admin
from django.contrib.auth.models import User, Group

from rules.models import Market

# Register your models here.

admin.site.register(Market)
admin.site.unregister(User)
admin.site.unregister(Group)