from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('tours.api.urls')),  # API endpoints
    path('', include('tours.urls')),  # Frontend web routes
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls'))) 