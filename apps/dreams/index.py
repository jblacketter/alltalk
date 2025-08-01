from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from .models import Dream


@register(Dream)
class DreamIndex(AlgoliaIndex):
    """Algolia index for community dreams."""
    
    # Fields to include in the index
    fields = [
        'title',
        'description',
        'mood',
        'themes',
        'symbols',
        'dream_date',
        'created_at',
        'lucidity_level',
    ]
    
    # Custom primary key field
    custom_objectID = 'id'
    
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
        return {
            'user_username': obj.user.username,
            'user_id': str(obj.user.id),
            'has_voice': bool(obj.voice_recording),
            '_tags': self._get_tags(obj),
        }
    
    def _should_index(self, obj):
        """Custom should_index method to handle the check properly."""
        return obj.privacy_level == 'community'
    
    def get_model_obj_id(self, obj):
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