
from django.urls import path
from . import views

urlpatterns = [
    path('register-voice/', views.register_voice),
    path('delete-voice/', views.delete_voice),
    path('generate_voice/', views.generate_voice),
    path('get-usage-summary/', views.get_usage_summary),
    path('unique-voices/', views.unique_voices),
    path('current-plan/', views.current_plan),
    path('check-status/', views.check_status),
    path('set-expiry-date/', views.set_expiry_date),
]
