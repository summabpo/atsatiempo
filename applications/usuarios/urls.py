from django.urls import path
from .views import login



urlpatterns = [
    path('', login.login_view, name='login'),
    path('logout_view/', login.logout_view, name='logout'),
    path('signup/', login.signup_view, name='signup'),
]