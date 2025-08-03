#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Show current migration status
echo "Current migration status:"
python manage.py showmigrations dreams

# Apply any outstanding database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Double-check DreamImage table exists
echo "Verifying DreamImage table..."
python manage.py fix_dreamimage_migration || true

# Show migration status after
echo "Migration status after:"
python manage.py showmigrations dreams

# Initialize Algolia index (only if configured)
if [ ! -z "$ALGOLIA_APPLICATION_ID" ]; then
    echo "Initializing Algolia search index..."
    python manage.py init_algolia_index || echo "Algolia index initialization skipped"
fi

echo "Build completed successfully!"