from rest_framework import serializers
from .models import Grid, GridRegion, GridNode, Measures


class GridSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grid
        fields = ['id', 'name']


class GridRegionSerializer(serializers.ModelSerializer):
    grid_name = serializers.CharField(source='grid.name', read_only=True)
    
    class Meta:
        model = GridRegion
        fields = ['id', 'grid', 'grid_name', 'name']


class GridNodeSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    grid_name = serializers.CharField(source='region.grid.name', read_only=True)
    
    class Meta:
        model = GridNode
        fields = ['id', 'region', 'region_name', 'grid_name', 'name']


class MeasuresSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source='node.name', read_only=True)
    region_name = serializers.CharField(source='node.region.name', read_only=True)
    grid_name = serializers.CharField(source='node.region.grid.name', read_only=True)
    
    class Meta:
        model = Measures
        fields = [
            'id', 'node', 'node_name', 'region_name', 'grid_name',
            'timestamp', 'collected_at', 'value'
        ]


class MeasuresQuerySerializer(serializers.Serializer):
    """Serializer for querying measures with date range filters"""
    start_datetime = serializers.DateTimeField(required=True)
    end_datetime = serializers.DateTimeField(required=True)
    collected_datetime = serializers.DateTimeField(required=False)
    node_id = serializers.UUIDField(required=False)
    grid_id = serializers.UUIDField(required=False)
    region_id = serializers.UUIDField(required=False)


class MeasuresResponseSerializer(serializers.ModelSerializer):
    """Serializer for measures API response with additional context"""
    node_name = serializers.CharField(source='node.name', read_only=True)
    region_name = serializers.CharField(source='node.region.name', read_only=True)
    grid_name = serializers.CharField(source='node.region.grid.name', read_only=True)
    
    class Meta:
        model = Measures
        fields = [
            'id', 'node_name', 'region_name', 'grid_name',
            'timestamp', 'collected_at', 'value'
        ] 