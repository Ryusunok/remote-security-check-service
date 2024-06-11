from django.urls import path
from myapp import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('', views.home, name='home'),
    path('check-username/', views.check_username, name='check_username'),
    path('service-check/', views.service_check, name='service-check'),
    path('service-result/', views.service_result, name='service-result'),
    path('service-ready/', views.service_ready, name='service-ready')
]
