from django.core.management.base import BaseCommand
from django.conf import settings
from apps.dreams.models import Dream
from algoliasearch_django import get_adapter, clear_index, reindex_all
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize or rebuild Algolia search index for community dreams'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear the index before reindexing',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to index at once',
        )
    
    def handle(self, *args, **options):
        if not settings.ALGOLIA.get('APPLICATION_ID'):
            self.stdout.write(
                self.style.WARNING('Algolia not configured. Skipping index initialization.')
            )
            return
        
        try:
            # Get the model adapter
            model = Dream
            
            if options['clear']:
                self.stdout.write('Clearing existing index...')
                clear_index(model)
                self.stdout.write(self.style.SUCCESS('Index cleared.'))
            
            # Get community dreams count
            community_dreams = Dream.objects.filter(privacy_level='community')
            count = community_dreams.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.WARNING('No community dreams found to index.')
                )
                return
            
            self.stdout.write(f'Indexing {count} community dreams...')
            
            # Reindex all community dreams
            reindex_all(model, batch_size=options['batch_size'])
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully indexed {count} dreams to Algolia!')
            )
            
        except Exception as e:
            logger.error(f"Error initializing Algolia index: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )