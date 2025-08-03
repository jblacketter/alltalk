from django.conf import settings
from algoliasearch.search.client import SearchClientSync
import logging

logger = logging.getLogger(__name__)


class AlgoliaSearchService:
    """Service for handling Algolia search operations."""
    
    def __init__(self):
        self.app_id = settings.ALGOLIA.get('APPLICATION_ID')
        self.api_key = settings.ALGOLIA.get('API_KEY')
        self.search_key = settings.ALGOLIA.get('SEARCH_API_KEY')
        self.index_prefix = settings.ALGOLIA.get('INDEX_PREFIX', 'dreamjournal')
        
        if self.app_id and self.api_key:
            self.client = SearchClientSync(self.app_id, self.api_key)
            self.search_client = SearchClientSync(self.app_id, self.search_key)
            self.enabled = True
        else:
            logger.warning("Algolia credentials not found. Search functionality disabled.")
            self.enabled = False
    
    def get_index_name(self, model_name='dreams'):
        """Get the full index name with prefix."""
        return f"{self.index_prefix}_{model_name}"
    
    def search_dreams(self, query, filters=None, facets=None, page=0, per_page=20):
        """Search for dreams in Algolia."""
        if not self.enabled:
            return {'hits': [], 'nbHits': 0, 'page': 0, 'nbPages': 0}
        
        try:
            index = self.search_client.init_index(self.get_index_name())
            
            search_params = {
                'query': query,
                'hitsPerPage': per_page,
                'page': page,
            }
            
            if filters:
                search_params['filters'] = filters
            
            if facets:
                search_params['facets'] = facets
            
            return index.search(**search_params)
            
        except Exception as e:
            logger.error(f"Algolia search error: {e}")
            return {'hits': [], 'nbHits': 0, 'page': 0, 'nbPages': 0}
    
    def update_dream_index(self, dream):
        """Update a single dream in the index."""
        if not self.enabled or not dream.is_public_dream():
            return
        
        try:
            # Manually create the record to ensure proper serialization
            index = self.client.init_index(self.get_index_name())
            
            # Build the record with properly serialized data
            record = {
                'objectID': str(dream.id),  # Convert UUID to string
                'title': dream.title or '',
                'description': dream.description or '',
                'mood': dream.mood or '',
                'themes': dream.themes or [],
                'symbols': dream.symbols or [],
                'lucidity_level': dream.lucidity_level,
                'dream_date': dream.dream_date.isoformat() if dream.dream_date else None,
                'created_at': dream.created_at.isoformat() if dream.created_at else None,
                'user_username': dream.user.username,
                'user_id': str(dream.user.id),
                'has_voice': bool(dream.voice_recording),
            }
            
            # Save the record
            index.save_object(record)
            logger.info(f"Dream {dream.id} indexed in Algolia")
            
        except Exception as e:
            logger.error(f"Error updating dream {dream.id} in Algolia: {e}")
    
    def remove_dream_from_index(self, dream):
        """Remove a dream from the index."""
        if not self.enabled:
            return
        
        try:
            index = self.client.init_index(self.get_index_name())
            # Use string version of UUID for objectID
            index.delete_object(str(dream.id))
            logger.info(f"Dream {dream.id} removed from Algolia")
        except Exception as e:
            logger.error(f"Error removing dream {dream.id} from Algolia: {e}")
    
    def get_search_settings(self):
        """Get search configuration for frontend."""
        if not self.enabled:
            return None
        
        return {
            'appId': self.app_id,
            'apiKey': self.search_key,
            'indexName': self.get_index_name(),
            'enabled': True,
        }


# Singleton instance
algolia_search = AlgoliaSearchService()