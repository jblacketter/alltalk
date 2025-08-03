from algoliasearch_django import AlgoliaIndex
# Don't use the register decorator - it causes automatic indexing
# from algoliasearch_django.decorators import register
from .models import Dream
import datetime
import uuid


# @register(Dream)  # DISABLED - This was causing UUID serialization errors
class DreamIndex(AlgoliaIndex):
    """Algolia index for community dreams."""
    
    # Fields to include in the index - don't include 'id' here
    fields = [
        'title',
        'description',
        'mood',
        'themes',
        'symbols',
        # 'dream_date',  # We'll handle date serialization manually
        # 'created_at',  # We'll handle date serialization manually
        'lucidity_level',
    ]
    
    # Don't use custom_objectID with UUID - we'll handle it in get_objectID
    # custom_objectID = 'id'
    
    # Settings for search
    settings = {
        'searchableAttributes': [
            'title',
            'description',
            'themes',
            'symbols',
            'mood',
            'user_username',
        ],
        'attributesForFaceting': [
            'searchable(mood)',
            'searchable(themes)',
            'lucidity_level',
            'user_username',
        ],
        'customRanking': [
            'desc(created_at)',
        ],
        'highlightPreTag': '<em class="search-highlight">',
        'highlightPostTag': '</em>',
    }
    
    # Index name
    index_name = 'dreams'
    
    # Only index public/community dreams
    should_index = 'is_public_dream'
    
    def get_queryset(self):
        """Only return community dreams for indexing."""
        return self.model.objects.filter(privacy_level='community')
    
    def get_extra_data(self, obj):
        """Add extra data to the index."""
        # Convert dates to ISO format strings
        dream_date = obj.dream_date.isoformat() if obj.dream_date else None
        created_at = obj.created_at.isoformat() if obj.created_at else None
        
        return {
            'user_username': obj.user.username,
            'user_id': str(obj.user.id) if isinstance(obj.user.id, uuid.UUID) else obj.user.id,
            'has_voice': bool(obj.voice_recording),
            '_tags': self._get_tags(obj),
            'dream_date': dream_date,
            'created_at': created_at,
            'objectID': str(obj.id),  # Explicitly set objectID as string
        }
    
    def _should_index(self, obj):
        """Custom should_index method to handle the check properly."""
        return obj.privacy_level == 'community'
    
    def get_objectID(self, obj):
        """Return the object ID as a string to handle UUID primary keys."""
        return str(obj.id)
    
    def _get_tags(self, obj):
        """Generate searchable tags."""
        tags = []
        if obj.themes:
            tags.extend(obj.themes)
        if obj.mood:
            tags.append(obj.mood)
        if obj.lucidity_level > 5:
            tags.append('lucid')
        if obj.voice_recording:
            tags.append('voice')
        return tags