from django.urls import path, include

from api import urls as api_urls


urlpatterns = [
    path('api/v1/', include(api_urls))
]
