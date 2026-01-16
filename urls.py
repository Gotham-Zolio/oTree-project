"""
Custom URL configuration for oTree
"""

# 直接使用 otree.urls 中的 URL patterns
try:
    from otree.urls import urlpatterns
except ImportError:
    # 如果直接导入失败，尝试通过 path 包含
    from django.urls import path, include
    urlpatterns = [
        path('', include('otree.urls')),
    ]
