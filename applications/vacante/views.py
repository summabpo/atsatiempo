# Importaciones necesarias para las vistas de vacantes
try:
    from .views.admin_views import (
        create_vacanty,
        list_vacanty_all,
        list_vacanty_from_client,
        create_vacanty_from_client,
        edit_vacanty_from_client,
        vacanty_management_from_client
    )
except ImportError:
    # Si no se pueden importar, crear funciones dummy
    def create_vacanty(*args, **kwargs): pass
    def list_vacanty_all(*args, **kwargs): pass
    def list_vacanty_from_client(*args, **kwargs): pass
    def create_vacanty_from_client(*args, **kwargs): pass
    def edit_vacanty_from_client(*args, **kwargs): pass
    def vacanty_management_from_client(*args, **kwargs): pass

try:
    from .views.client_views import (
        create_vacanty_v2,
        list_vacanty_all as client_list_vacanty_all,
        detail_vacancy,
        detail_vacancy_interview,
        detail_vacancy_assign
    )
except ImportError:
    # Si no se pueden importar, crear funciones dummy
    def create_vacanty_v2(*args, **kwargs): pass
    def client_list_vacanty_all(*args, **kwargs): pass
    def detail_vacancy(*args, **kwargs): pass
    def detail_vacancy_interview(*args, **kwargs): pass
    def detail_vacancy_assign(*args, **kwargs): pass

try:
    from .views.client_analyst_views import list_assigned_vacancies
except ImportError:
    def list_assigned_vacancies(*args, **kwargs): pass

try:
    from .views.client_analyst_internal_views import (
        list_assigned_vacancies as internal_list_assigned_vacancies,
        detail_vacancy as internal_detail_vacancy
    )
except ImportError:
    def internal_list_assigned_vacancies(*args, **kwargs): pass
    def internal_detail_vacancy(*args, **kwargs): pass

try:
    from .views.candidate_views import (
        apply_vacancy,
        apply_vacancy_detail,
        vacancy_available
    )
except ImportError:
    def apply_vacancy(*args, **kwargs): pass
    def apply_vacancy_detail(*args, **kwargs): pass
    def vacancy_available(*args, **kwargs): pass

# Crear objetos para las importaciones en urls.py
admin_views = type('admin_views', (), {
    'create_vacanty': create_vacanty,
    'list_vacanty_all': list_vacanty_all,
    'list_vacanty_from_client': list_vacanty_from_client,
    'create_vacanty_from_client': create_vacanty_from_client,
    'edit_vacanty_from_client': edit_vacanty_from_client,
    'vacanty_management_from_client': vacanty_management_from_client
})

client_views = type('client_views', (), {
    'create_vacanty_v2': create_vacanty_v2,
    'list_vacanty_all': client_list_vacanty_all,
    'detail_vacancy': detail_vacancy,
    'detail_vacancy_interview': detail_vacancy_interview,
    'detail_vacancy_assign': detail_vacancy_assign
})

client_analyst_views = type('client_analyst_views', (), {
    'list_assigned_vacancies': list_assigned_vacancies
})

client_analyst_internal_views = type('client_analyst_internal_views', (), {
    'list_assigned_vacancies': internal_list_assigned_vacancies,
    'detail_vacancy': internal_detail_vacancy
})

candidate_views = type('candidate_views', (), {
    'apply_vacancy': apply_vacancy,
    'apply_vacancy_detail': apply_vacancy_detail,
    'vacancy_available': vacancy_available
})

# Importar VacanteViews y EntrevistaView
try:
    from .views.VacanteViews import VacanteViews
except ImportError:
    VacanteViews = None

try:
    from .views.EntrevistaView import EntrevistaView
except ImportError:
    EntrevistaView = None 