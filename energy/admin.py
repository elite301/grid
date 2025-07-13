from django.contrib import admin
from .models import Grid, GridRegion, GridNode, Measures


@admin.register(Grid)
class GridAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(GridRegion)
class GridRegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'grid']
    list_filter = ['grid']
    search_fields = ['name', 'grid__name']


@admin.register(GridNode)
class GridNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'grid']
    list_filter = ['region__grid', 'region']
    search_fields = ['name', 'region__name', 'region__grid__name']
    
    def grid(self, obj):
        return obj.region.grid.name
    grid.short_description = 'Grid'


@admin.register(Measures)
class MeasuresAdmin(admin.ModelAdmin):
    list_display = ['node', 'grid', 'region', 'timestamp', 'collected_at', 'value']
    list_filter = ['node__region__grid', 'node__region', 'timestamp', 'collected_at']
    search_fields = ['node__name', 'node__region__name', 'node__region__grid__name']
    date_hierarchy = 'timestamp'
    
    def grid(self, obj):
        return obj.node.region.grid.name
    grid.short_description = 'Grid'
    
    def region(self, obj):
        return obj.node.region.name
    region.short_description = 'Region'
