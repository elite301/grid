from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from energy.models import Grid, GridRegion, GridNode, Measures


class Command(BaseCommand):
    help = 'Seed the database with sample grid data and time series measurements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weeks',
            type=int,
            default=1,
            help='Number of weeks of data to generate (default: 1)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting data seeding...')
        
        # Create Grids
        grids = []
        for i in range(1, 4):
            grid, created = Grid.objects.get_or_create(
                name=f'Grid{i}'
            )
            grids.append(grid)
            if created:
                self.stdout.write(f'Created Grid: {grid.name}')
        
        # Create Grid Regions
        regions = []
        for grid in grids:
            for i in range(1, 4):
                region, created = GridRegion.objects.get_or_create(
                    grid=grid,
                    name=f'Region{i}'
                )
                regions.append(region)
                if created:
                    self.stdout.write(f'Created Region: {region.name} for {grid.name}')
        
        # Create Grid Nodes
        nodes = []
        for region in regions:
            for i in range(1, 4):
                node, created = GridNode.objects.get_or_create(
                    region=region,
                    name=f'Node{i}'
                )
                nodes.append(node)
                if created:
                    self.stdout.write(f'Created Node: {node.name} in {region.name}')
        
        # Generate time series data with evolution
        weeks = options['weeks']
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(weeks=weeks)
        
        self.stdout.write(f'Generating {weeks} week(s) of time series data...')
        
        # Generate hourly timestamps
        current_timestamp = start_date
        timestamps = []
        while current_timestamp <= end_date:
            timestamps.append(current_timestamp)
            current_timestamp += timedelta(hours=1)
        
        measures_created = 0
        
        for node in nodes:
            self.stdout.write(f'Generating data for {node.name}...')
            
            for timestamp in timestamps:

                collection_times = []
                current_collection = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                end_collection = current_collection + timedelta(days=1)
                while current_collection <= end_collection:
                    collection_times.append(current_collection)
                    current_collection += timedelta(hours=6)

                for collection_time in collection_times:        
                    # Create the measure
                    measure, created = Measures.objects.get_or_create(
                        node=node,
                        timestamp=timestamp,
                        collected_at=collection_time,
                        defaults={
                            'value': Decimal(str(round(random.uniform(0, 1000), 3)))
                        }
                    )
                    
                    if created:
                        measures_created += 1
                        
                        # Progress indicator
                        if measures_created % 100 == 0:
                            self.stdout.write(f'Created {measures_created} measures...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {measures_created} measures for {len(nodes)} nodes '
                f'over {weeks} week(s) with evolution support!'
            )
        )
        
        # Print some statistics
        total_measures = Measures.objects.count()
        latest_measure = Measures.objects.order_by('-timestamp').first()
        earliest_measure = Measures.objects.order_by('timestamp').first()
        
        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'- Total measures: {total_measures}')
        self.stdout.write(f'- Date range: {earliest_measure.timestamp} to {latest_measure.timestamp}')
        self.stdout.write(f'- Grids: {Grid.objects.count()}')
        self.stdout.write(f'- Regions: {GridRegion.objects.count()}')
        self.stdout.write(f'- Nodes: {GridNode.objects.count()}')
        
        # Show evolution example
        if total_measures > 0:
            sample_node = nodes[0]
            sample_timestamp = timestamps[0]
            evolution_measures = Measures.objects.filter(
                node=sample_node,
                timestamp=sample_timestamp
            ).order_by('collected_at')[:5]
            
            self.stdout.write(f'\nEvolution example for {sample_node.name} at {sample_timestamp}:')
            for measure in evolution_measures:
                self.stdout.write(
                    f'  Collected at {measure.collected_at}: {measure.value}'
                ) 