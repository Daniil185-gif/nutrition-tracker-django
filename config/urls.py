from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

handler404 = 'config.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipes.urls')),
    path('', include('users.urls')),
    path('', include('diary.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
