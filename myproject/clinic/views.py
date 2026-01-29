from django.shortcuts import render

def login_view(request):
    return render(request, 'clinic/login.html')

def dashboard(request):
    return render(request, 'clinic/dashboard.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Patient

def patients_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by('-created_at')
    
    if query:
        patients = patients.filter(
            Q(full_name__icontains=query) | 
            Q(phone__icontains=query)
        )
    
    paginator = Paginator(patients, 10)  # 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'clinic/patients_list.html', {
        'page_obj': page_obj,
        'query': query,
        'count': paginator.count
    })

def add_patient(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        notes = request.POST.get('notes')
        
        # Basic validation
        if not full_name or not phone or not age:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'clinic/add_patient.html')
            
        try:
            Patient.objects.create(
                full_name=full_name,
                phone=phone,
                age=age,
                gender=gender,
                notes=notes
            )
            messages.success(request, 'Patient added successfully.')
            return redirect('patients_list')
        except Exception as e:
            messages.error(request, f'Error adding patient: {e}')
            
    return render(request, 'clinic/add_patient.html')

def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        notes = request.POST.get('notes')
        
        if not full_name or not phone or not age:
            messages.error(request, 'Please fill in all required fields.')
        else:
            try:
                patient.full_name = full_name
                patient.phone = phone
                patient.age = age
                patient.gender = gender
                patient.notes = notes
                patient.save()
                messages.success(request, 'Patient updated successfully.')
                return redirect('patients_list')
            except Exception as e:
                messages.error(request, f'Error updating patient: {e}')
    
    return render(request, 'clinic/add_patient.html', {'patient': patient})

def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient deleted successfully.')
    return redirect('patients_list')

def patient_profile(request, id):
    patient = get_object_or_404(Patient, id=id)
    # Get last visit and appointments if models are related correctly
    visits = patient.visits.all().order_by('-visit_date')
    appointments = patient.appointments.filter(status='scheduled').order_by('date', 'time')
    
    return render(request, 'clinic/patient_profile.html', {
        'patient': patient,
        'visits': visits,
        'appointments': appointments
    })

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
