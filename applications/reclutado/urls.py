from django.urls import path
from applications.reclutado.views import client_views, client_analyst_internal_views, candidate_views, api_views, client_recruiter_views, admin_views



url_principal = 'reclutado/'

urlpatterns = [

    #all
    

    #client_user
    path( url_principal+'listado/<int:pk>/', client_views.detail_vacancy_recruited, name='vacantes_reclutados_cliente'),
    path( url_principal+'detalle/<int:pk>/', client_views.detail_recruited, name='reclutados_detalle_cliente'),

    #analyst_internal_user
    path( url_principal+'listado/analista/<int:pk>/', client_analyst_internal_views.detail_vacancy_recruited, name='reclutados_analista_interno'),
    path( url_principal+'gestion/<int:pk>/', client_analyst_internal_views.detail_recruited, name='reclutados_detalle_analista_interno'),

    #candidate_user
    path( url_principal+'aplicar_vacante/<int:pk>/', candidate_views.confirm_apply_vacancy_recruited, name='reclutados_confirmar_aplicar_candidato'),
    path( url_principal+'aplicar_vacante/aplicar/<int:pk>/', candidate_views.apply_vacancy_recruited_candidate, name='reclutados_aplicar_candidato'),

    #api
    path( url_principal+'api/buscar_candidato/', api_views.api_candidate_document, name='api_canidate_document'),

    #reclutador
    path( url_principal+'vacantes_asignadas/', client_recruiter_views.vacancies_assigned_recruiter, name='vacantes_asignadas_reclutador'),
    path( url_principal+'vacantes_asignadas/gestionar/<int:pk>/<int:vacante_id>/', client_recruiter_views.vacancies_assigned_recruiter_detail, name='vacantes_gestion_reclutador'),
    path( url_principal+'detalle/reclutado/<int:pk>/', client_recruiter_views.detail_recruited, name='reclutados_detalle_reclutador'),
    path( url_principal+'crear_entrevistas_multiples/<int:pk>/<int:vacante_id>/', client_recruiter_views.crear_entrevistas_multiples, name='crear_entrevistas_multiples'),

    #admin_user
    path( url_principal+'resultado/<int:pk>/', admin_views.detail_aplicacion_vacante, name='reclutados_detalle_admin'),
    path( url_principal+'reporte/pdf/<int:pk>/', admin_views.generar_reporte_pdf, name='reclutados_reporte_pdf_admin'),

    #test
    path( url_principal+'test/<int:pk>/', candidate_views.test_match, name='test_match'),

]