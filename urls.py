from django.urls import path, include

def get_urlpatterns():
    # 延迟导入以避免循环导入问题
    import otree.urls
    return [
        path('', include('otree.urls')),
    ]

urlpatterns = get_urlpatterns()
