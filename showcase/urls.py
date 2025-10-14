from django.urls import path
from . import views

app_name = 'showcase'

urlpatterns = [
    # Homepage (landing page)
    path('', views.landing_page, name='landing'),
    # Main dashboard (demo version)
    path('dashboard/', views.dashboard, name='dashboard_demo'),  
    # API endpoints
    path('api/create-task/', views.create_advanced_task_demo, name='create_demo_task'),
    path('api/create-advanced-task/', views.create_advanced_task_demo, name='create_advanced_task'),
    path('api/add-telegram-user/', views.create_telegram_user_demo, name='create_telegram_user'),
]
