from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max, Q
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

from .models import Grid, GridRegion, GridNode, Measures
from .serializers import (
    GridSerializer, GridRegionSerializer, GridNodeSerializer,
    MeasuresSerializer, MeasuresQuerySerializer, MeasuresResponseSerializer
)


class GridViewSet(viewsets.ModelViewSet):
    """ViewSet for Grid operations"""
    queryset = Grid.objects.all()
    serializer_class = GridSerializer


class GridRegionViewSet(viewsets.ModelViewSet):
    """ViewSet for GridRegion operations"""
    queryset = GridRegion.objects.select_related('grid').all()
    serializer_class = GridRegionSerializer


class GridNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for GridNode operations"""
    queryset = GridNode.objects.select_related('region', 'region__grid').all()
    serializer_class = GridNodeSerializer


class MeasuresViewSet(viewsets.ModelViewSet):
    """ViewSet for Measures operations"""
    queryset = Measures.objects.select_related('node', 'node__region', 'node__region__grid').all()
    serializer_class = MeasuresSerializer


class MeasuresAPIView(APIView):
    """
    API endpoint for querying measures with time series evolution support.
    
    This API supports two modes:
    1. Latest values: Returns the latest value for each timestamp in the date range
    2. Specific collection time: Returns values corresponding to a specific collected_datetime
    """
    
    def get(self, request):
        """GET endpoint for querying measures"""
        serializer = MeasuresQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        start_datetime = data['start_datetime']
        end_datetime = data['end_datetime']
        collected_datetime = data.get('collected_datetime')
        node_id = data.get('node_id')
        grid_id = data.get('grid_id')
        region_id = data.get('region_id')
        
        # Build base queryset
        queryset = Measures.objects.select_related(
            'node', 'node__region', 'node__region__grid'
        ).filter(
            timestamp__gte=start_datetime,
            timestamp__lte=end_datetime
        )
        
        # Apply filters
        if node_id:
            queryset = queryset.filter(node_id=node_id)
        if grid_id:
            queryset = queryset.filter(node__region__grid_id=grid_id)
        if region_id:
            queryset = queryset.filter(node__region_id=region_id)
        
        if collected_datetime:
            # Mode 2: Return values for specific collected_datetime
            queryset = queryset.filter(collected_at=collected_datetime)
        else:
            # Mode 1: Return latest values for each timestamp
            # This is a complex query that gets the latest collected_at for each node/timestamp combination
            latest_collected = queryset.values('node', 'timestamp').annotate(
                latest_collected=Max('collected_at')
            )
            
            # Build the filter for latest collected_at values
            latest_filters = Q()
            for item in latest_collected:
                latest_filters |= (
                    Q(node_id=item['node']) & 
                    Q(timestamp=item['timestamp']) & 
                    Q(collected_at=item['latest_collected'])
                )
            
            queryset = queryset.filter(latest_filters)
        
        # Order by timestamp and node for consistent results
        queryset = queryset.order_by('timestamp', 'node__name')
        
        # Serialize the results
        serializer = MeasuresResponseSerializer(queryset, many=True)
        
        return Response({
            'count': len(serializer.data),
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'collected_datetime': collected_datetime,
            'results': serializer.data
        })


class MeasuresEvolutionAPIView(APIView):
    """
    API endpoint specifically for querying measures with evolution support.
    Returns the value corresponding to the collected_datetime for each timestamp in the date range.
    """
    
    def get(self, request):
        """GET endpoint for querying measures with evolution"""
        serializer = MeasuresQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        start_datetime = data['start_datetime']
        end_datetime = data['end_datetime']
        collected_datetime = data.get('collected_datetime')
        node_id = data.get('node_id')
        grid_id = data.get('grid_id')
        region_id = data.get('region_id')
        
        if not collected_datetime:
            return Response(
                {'error': 'collected_datetime is required for evolution queries'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build queryset
        queryset = Measures.objects.select_related(
            'node', 'node__region', 'node__region__grid'
        ).filter(
            timestamp__gte=start_datetime,
            timestamp__lte=end_datetime,
            collected_at=collected_datetime
        )
        
        # Apply filters
        if node_id:
            queryset = queryset.filter(node_id=node_id)
        if grid_id:
            queryset = queryset.filter(node__region__grid_id=grid_id)
        if region_id:
            queryset = queryset.filter(node__region_id=region_id)
        
        # Order by timestamp and node
        queryset = queryset.order_by('timestamp', 'node__name')
        
        # Serialize the results
        serializer = MeasuresResponseSerializer(queryset, many=True)
        
        return Response({
            'count': len(serializer.data),
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'collected_datetime': collected_datetime,
            'evolution_type': 'specific_collection_time',
            'results': serializer.data
        })


class DashboardAPIView(APIView):
    """Dashboard API for overview statistics"""
    
    def get(self, request):
        """GET endpoint for dashboard statistics"""
        total_grids = Grid.objects.count()
        total_regions = GridRegion.objects.count()
        total_nodes = GridNode.objects.count()
        total_measures = Measures.objects.count()
        
        # Get latest measure timestamp
        latest_measure = Measures.objects.order_by('-timestamp').first()
        latest_timestamp = latest_measure.timestamp if latest_measure else None
        
        # Get measures count for last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        measures_last_24h = Measures.objects.filter(
            collected_at__gte=yesterday
        ).count()
        
        return Response({
            'statistics': {
                'total_grids': total_grids,
                'total_regions': total_regions,
                'total_nodes': total_nodes,
                'total_measures': total_measures,
                'measures_last_24h': measures_last_24h,
                'latest_measure_timestamp': latest_timestamp,
            }
        })
