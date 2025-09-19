from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include(('applications.candidato.urls', 'candidatos'))),
    re_path('', include(('applications.cliente.urls', 'clientes'))),
    re_path('', include(('applications.common.urls', 'common'))),
    re_path('', include(('applications.usuarios.urls', 'accesses'))),
    re_path('', include(('applications.vacante.urls', 'vacantes'))),
    re_path('', include(('applications.entrevista.urls', 'entrevistas'))),

    #re_path('', include(('applications.pruebas_psi.urls', 'pruebas_psi'))),
    path('pruebas_psi/', include(('applications.pruebas_psi.urls', 'pruebas_psi'))),

    re_path('', include(('applications.reclutado.urls', 'reclutados'))),

    
    # re_path('', include(('applications.pruebas_psi.urls', 'pruebas_psi'))),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('debug/', include(debug_toolbar.urls)),
#     ] + urlpatterns