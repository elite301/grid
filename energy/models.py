from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Grid(models.Model):
    """
    Grid model representing TSO/ISOs (Transmission System Operators/Independent System Operators)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'grids'
        verbose_name = 'Grid'
        verbose_name_plural = 'Grids'

    def __str__(self):
        return self.name


class GridRegion(models.Model):
    """
    Grid Region model with many-to-one relationship with Grid
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name='regions')
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'grid_regions'
        verbose_name = 'Grid Region'
        verbose_name_plural = 'Grid Regions'
        unique_together = ['grid', 'name']

    def __str__(self):
        return f"{self.grid.name} - {self.name}"


class GridNode(models.Model):
    """
    Grid Node model with many-to-one relationship with GridRegion
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(GridRegion, on_delete=models.CASCADE, related_name='nodes')
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'grid_nodes'
        verbose_name = 'Grid Node'
        verbose_name_plural = 'Grid Nodes'
        unique_together = ['region', 'name']

    def __str__(self):
        return f"{self.region.grid.name} - {self.region.name} - {self.name}"


class Measures(models.Model):
    """
    Measures model for storing hourly time series values with evolution support.
    This table supports storing the evolution of time series data where values
    can change over time for the same timestamp.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(GridNode, on_delete=models.CASCADE, related_name='measures')
    
    # The timestamp for which this measurement is valid
    timestamp = models.DateTimeField(db_index=True)
    
    # The datetime when this measurement was collected/updated
    collected_at = models.DateTimeField(db_index=True)
    
    # The actual measurement value (in kW, kWh, or other energy units)
    value = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(-999999999.999), MaxValueValidator(999999999.999)]
    )

    class Meta:
        db_table = 'measures'
        verbose_name = 'Measure'
        verbose_name_plural = 'Measures'
        # Composite index for efficient querying by node, timestamp, and collected_at
        indexes = [
            models.Index(fields=['node', 'timestamp', 'collected_at']),
            models.Index(fields=['timestamp', 'collected_at']),
            models.Index(fields=['node', 'timestamp']),
        ]
        # Ensure we don't have duplicate measurements for the same node, timestamp, and collected_at
        unique_together = ['node', 'timestamp', 'collected_at']

    def __str__(self):
        return f"{self.node} - {self.timestamp} - {self.value}"

    @property
    def grid_name(self):
        return self.node.region.grid.name

    @property
    def region_name(self):
        return self.node.region.name

    @property
    def node_name(self):
        return self.node.name
