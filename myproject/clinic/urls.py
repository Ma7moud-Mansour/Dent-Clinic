from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:id>/edit/', views.edit_patient, name='edit_patient'),
    path('patients/<int:id>/delete/', views.delete_patient, name='delete_patient'),
    path('patients/<int:id>/', views.patient_profile, name='patient_profile'),
    path('visits/', views.visits, name='visits'),
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/<int:id>/', views.invoice_detail, name='invoice_detail'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
]
