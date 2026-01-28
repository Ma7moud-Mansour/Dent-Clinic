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
