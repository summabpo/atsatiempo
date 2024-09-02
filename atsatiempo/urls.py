from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include(('applications.candidato.urls', 'candidatos'))),
    re_path('', include(('applications.cliente.urls', 'clientes'))),
    re_path('', include(('applications.common.urls', 'common'))),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
