from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = 'Fix DreamImage migration if table is missing'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if dream_images table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'dream_images'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                self.stdout.write(self.style.WARNING('Table dream_images does not exist. Running migration...'))
                try:
                    # Run the specific migration
                    call_command('migrate', 'dreams', '0004')
                    self.stdout.write(self.style.SUCCESS('Successfully created dream_images table'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error running migration: {e}'))
                    # Try running all migrations
                    self.stdout.write(self.style.WARNING('Attempting to run all pending migrations...'))
                    call_command('migrate')
            else:
                self.stdout.write(self.style.SUCCESS('Table dream_images already exists'))