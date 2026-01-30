from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:id>/edit/', views.edit_patient, name='edit_patient'),
    path('patients/<int:id>/delete/', views.delete_patient, name='delete_patient'),
    path('patients/<int:patient_id>/xray/add/', views.add_xray, name='add_xray'),
    path('patients/<int:patient_id>/notes/update/', views.update_medical_notes, name='update_medical_notes'),
    path('patients/<int:id>/', views.patient_profile, name='patient_profile'),
    path('visits/', views.visits, name='visits'),
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:id>/status/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/<int:id>/', views.invoice_detail, name='invoice_detail'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/users/', views.users_list, name='users_list'),
    path('settings/users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('settings/users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('settings/users/<int:pk>/password/', views.change_user_password, name='change_user_password'),
]
