from django.contrib import admin
from apis.models import DemoTable


class DemoTableAdmin(admin.ModelAdmin):
    list_display = ("record_id", "record_name")
    readonly_fields = ("record_id",)


admin.site.register(DemoTable, DemoTableAdmin)
