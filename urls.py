"""
oTree URL configuration
Dynamically import urlpatterns from otree to avoid circular imports
"""
import sys
from importlib import import_module

def get_urlpatterns():
    """
    Delayed import of oTree URL patterns to avoid circular import issues
    """
    try:
        # Try to get urlpatterns from otree.urls
        otree_urls = import_module('otree.urls')
        if hasattr(otree_urls, 'urlpatterns'):
            return otree_urls.urlpatterns
    except ImportError:
        pass
    
    # Fallback: use path-based include
    from django.urls import path, include
    return [
        path('', include('otree.urls')),
    ]

# Only compute urlpatterns when accessed, not at import time
class LazyURLPatterns(list):
    def __init__(self):
        self._loaded = False
    
    def __iter__(self):
        if not self._loaded:
            self.extend(get_urlpatterns())
            self._loaded = True
        return super().__iter__()
    
    def __getitem__(self, key):
        if not self._loaded:
            self.extend(get_urlpatterns())
            self._loaded = True
        return super().__getitem__(key)

urlpatterns = LazyURLPatterns()
