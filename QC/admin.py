from django.contrib import admin

from .models import ExecutionStats

class ExecutionStatsAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'details')

admin.site.register(ExecutionStats, ExecutionStatsAdmin)