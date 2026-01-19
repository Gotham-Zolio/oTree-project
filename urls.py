"""
oTree URL configuration
"""

# Import oTree URLs after Django is fully initialized
from django.urls import path, include

# Use oTree's URL patterns
urlpatterns = [
    path('', include('otree.urls')),
]
