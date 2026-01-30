from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Helper to handle "Remember Me"
            if not request.POST.get('remember_me'):
                # Session expires on browser close
                request.session.set_expiry(0)
            # Else: uses default session expiry (typically 2 weeks)
            
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            return render(request, 'clinic/login.html', {'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'})
            
    return render(request, 'clinic/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'clinic/dashboard.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Patient, Appointment
from datetime import date, datetime

@login_required
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

@login_required
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

@login_required
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

@login_required
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient deleted successfully.')
    return redirect('patients_list')

@login_required
def add_xray(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        image = request.FILES.get('image')
        notes = request.POST.get('notes')
        
        if image:
            try:
                # Use string reference to model name to avoid circular import if needed, 
                # but models are in same app so direct import works.
                from .models import DentalXRay 
                DentalXRay.objects.create(
                    patient=patient,
                    image=image,
                    notes=notes
                )
                messages.success(request, 'X-Ray uploaded successfully.')
            except Exception as e:
                messages.error(request, f'Error uploading X-Ray: {e}')
        else:
            messages.error(request, 'Please select an image.')
            
    return redirect('patient_profile', id=patient_id)

@login_required
def update_medical_notes(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        notes = request.POST.get('notes')
        patient.notes = notes
        patient.save()
        messages.success(request, 'Medical notes updated successfully.')
    return redirect('patient_profile', id=patient_id)

@login_required
def patient_profile(request, id):
    patient = get_object_or_404(Patient, id=id)
    
    # "Visits" are now completed appointments
    visits = Appointment.objects.filter(
        patient=patient, 
        status='completed'
    ).order_by('-date', '-time')
    
    # "Appointments" are scheduled and in the future/today
    appointments = Appointment.objects.filter(
        patient=patient, 
        status='scheduled',
        date__gte=date.today()
    ).order_by('date', 'time')
    
    latest_xray = patient.xrays.last()
    
    return render(request, 'clinic/patient_profile.html', {
        'patient': patient,
        'visits': visits,
        'appointments': appointments,
        'latest_xray': latest_xray
    })

@login_required
def visits(request):
    return render(request, 'clinic/visits.html')



@login_required
def appointments_list(request):
    selected_date_str = request.GET.get('date')
    search_query = request.GET.get('q', '')
    
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = date.today()
        
    appointments = Appointment.objects.filter(date=selected_date).order_by('time')
    
    if search_query:
        appointments = appointments.filter(patient__full_name__icontains=search_query)
        
    return render(request, 'clinic/appointments_list.html', {
        'appointments': appointments,
        'selected_date': selected_date,
        'today': date.today(),
        'search_query': search_query
    })

@login_required
def add_appointment(request):
    patients = Patient.objects.all()
    
    if request.method == 'POST':
        patient_name_input = request.POST.get('patient_name')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        notes = request.POST.get('notes')
        
        # Validations
        if not patient_name_input or not date_str or not time_str:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'clinic/add_appointment.html', {'patients': patients})
            
        # Parse patient (Assuming input format "Name - #ID" or just "Name")
        patient = None
        if " - #" in patient_name_input:
            try:
                p_id = patient_name_input.split(" - #")[-1]
                patient = Patient.objects.get(id=p_id)
            except:
                pass
        
        if not patient:
            # Fallback search by exact name
            patient = Patient.objects.filter(full_name__iexact=patient_name_input).first()
            
        if not patient:
            messages.error(request, 'Patient not found. Please select a valid patient.')
            return render(request, 'clinic/add_appointment.html', {'patients': patients})
            
        try:
            Appointment.objects.create(
                patient=patient,
                date=date_str,
                time=time_str,
                notes=notes,
                status='scheduled'
            )
            messages.success(request, 'Appointment scheduled successfully.')
            return redirect('appointments_list')
        except Exception as e:
            messages.error(request, f'Error scheduling appointment: {e}')
            
    return render(request, 'clinic/add_appointment.html', {
        'patients': patients
    })

@login_required
def update_appointment_status(request, id, status):
    appointment = get_object_or_404(Appointment, id=id)
    if status in ['scheduled', 'completed', 'cancelled']:
        appointment.status = status
        appointment.save()
        messages.success(request, f'Appointment marked as {status}.')
    return redirect('appointments_list')

@login_required
def invoices_list(request):
    return render(request, 'clinic/invoices_list.html')

@login_required
def add_invoice(request):
    return render(request, 'clinic/add_invoice.html')

@login_required
def invoice_detail(request, id):
    return render(request, 'clinic/invoice_detail.html')

@login_required
def reports(request):
    return render(request, 'clinic/reports.html')

@login_required
def settings(request):
    return render(request, 'clinic/settings.html')
