from django.shortcuts import render

def login_view(request):
    return render(request, 'clinic/login.html')

def dashboard(request):
    return render(request, 'clinic/dashboard.html')

def patients_list(request):
    return render(request, 'clinic/patients_list.html')

def add_patient(request):
    return render(request, 'clinic/add_patient.html')

def patient_profile(request, id):
    return render(request, 'clinic/patient_profile.html')

def visits(request):
    return render(request, 'clinic/visits.html')

def appointments_list(request):
    return render(request, 'clinic/appointments_list.html')

def add_appointment(request):
    return render(request, 'clinic/add_appointment.html')

def invoices_list(request):
    return render(request, 'clinic/invoices_list.html')

def add_invoice(request):
    return render(request, 'clinic/add_invoice.html')

def invoice_detail(request, id):
    return render(request, 'clinic/invoice_detail.html')

def reports(request):
    return render(request, 'clinic/reports.html')

def settings(request):
    return render(request, 'clinic/settings.html')
