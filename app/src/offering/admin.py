from django.contrib import admin

from offering.models import DailyOffering

# Register your models here.
@admin.register(DailyOffering)
class DailyOfferingAdmin(admin.ModelAdmin):
   fields = ('position_name', 'date')
   list_display = ('__str__',)
   list_filter = ('date',)
   # search_fields = ('position_name',)
   readonly_fields = ('position_name', 'date')