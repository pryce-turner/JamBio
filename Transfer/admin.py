from django.contrib import admin

# Register your models here.
# from import_export import resources
from .models import ComponentInformation, TubeInformation, CoreData, ExecutionStats

class TubeSampleInline(admin.TabularInline):
    model = TubeInformation
    fields = ['tube_id', 'pool_id']

class CompSampleInline(admin.TabularInline):
    model = ComponentInformation
    fields = ['pool_id', 'sample_id', 'i5_index_name', 'i7_index_name']

class CoreSampleInline(admin.TabularInline):
    model = CoreData
    fields = ['pool_id', 'sample_id', 'i5_index_sequence', 'i7_index_sequence']

class TubeSampleAdmin(admin.ModelAdmin):
    list_display = ('tube_id', 'pool_id')

class ComponentAdmin(admin.ModelAdmin):
    list_display = ('pool_id', 'sample_id', 'i7_index_sequence', 'i5_index_sequence')

class CoreDataAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'i7_index_sequence', 'i5_index_sequence')

class ExecutionStatsAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'exec_date', 'exec_status', 'fail_reason')
    
admin.site.register(CoreData, CoreDataAdmin)
admin.site.register(ComponentInformation, ComponentAdmin)
admin.site.register(TubeInformation, TubeSampleAdmin)
admin.site.register(ExecutionStats, ExecutionStatsAdmin)
