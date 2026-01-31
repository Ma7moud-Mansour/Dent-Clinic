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
from .models import Patient, Appointment, User, Visit, Payment
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
def visits_list(request):
    # UI-only view - no backend logic yet
    return render(request, 'clinic/visits_list.html')



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
    visits = Visit.objects.all().order_by('-visit_date')
    return render(request, 'clinic/invoices_list.html', {'visits': visits})



@login_required
def add_invoice(request):
    try:
        patients = Patient.objects.all()
        doctors = User.objects.filter(role='doctor')
        
        if request.method == 'POST':
            patient_id = request.POST.get('patient')
            doctor_id = request.POST.get('doctor')
            visit_date = request.POST.get('date')
            description = request.POST.get('description')
            total_cost = request.POST.get('total_cost')
            notes = request.POST.get('notes')
            
            # DEBUG
            print(f"DEBUG: add_invoice POST: patient={patient_id}, doctor={doctor_id}, date={visit_date}, cost={total_cost}")
            
            if not patient_id or not visit_date or not total_cost:
                messages.error(request, 'Please fill in required fields.')
            else:
                try:
                    patient = Patient.objects.get(id=patient_id)
                    doctor = User.objects.get(id=doctor_id) if doctor_id else None
                    
                    visit = Visit.objects.create(
                        patient=patient,
                        doctor=doctor,
                        visit_date=visit_date,
                        description=description,
                        total_cost=total_cost,
                        notes=notes
                    )
                    
                    # Handle Payment Status
                    payment_status = request.POST.get('payment_status')
                    payment_method = request.POST.get('payment_method')
                    
                    if payment_status == 'paid':
                        Payment.objects.create(
                            visit=visit,
                            paid_amount=total_cost,
                            payment_method=payment_method
                        )
                    
                    messages.success(request, 'Invoice created successfully.')
                    return redirect('invoices_list')
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f'Error creating invoice: {e}')
                    
        return render(request, 'clinic/add_invoice.html', {
            'patients': patients,
            'doctors': doctors
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render(request, 'clinic/500_debug.html', {'error': str(e)})

@login_required
def edit_invoice(request, id):
    visit = get_object_or_404(Visit, id=id)
    patients = Patient.objects.all()
    doctors = User.objects.filter(role='doctor')
    
    if request.method == 'POST':
        visit_date = request.POST.get('date')
        description = request.POST.get('description')
        total_cost = request.POST.get('total_cost')
        notes = request.POST.get('notes')
        doctor_id = request.POST.get('doctor')
        
        try:
            visit.visit_date = visit_date
            visit.description = description
            visit.total_cost = total_cost
            visit.notes = notes
            if doctor_id:
                visit.doctor = User.objects.get(id=doctor_id)
            visit.save()
            
            # Handle Payment Status Update
            payment_status = request.POST.get('payment_status')
            payment_method = request.POST.get('payment_method')
            
            if payment_status == 'paid':
                # If marking as paid, and remaining amount > 0, pay the rest
                if visit.remaining_amount > 0:
                    Payment.objects.create(
                        visit=visit,
                        paid_amount=visit.remaining_amount,
                        payment_method=payment_method
                    )
            elif payment_status == 'unpaid':
                 # If marking as unpaid, remove all payments
                 visit.payments.all().delete()
            
            messages.success(request, 'Invoice updated successfully.')
            return redirect('invoices_list')
        except Exception as e:
            messages.error(request, f'Error updating invoice: {e}')
            
    return render(request, 'clinic/add_invoice.html', {
        'visit': visit,
        'patients': patients,
        'doctors': doctors,
        'is_edit': True
    })

@login_required
def delete_invoice(request, id):
    visit = get_object_or_404(Visit, id=id)
    if request.method == 'POST':
        visit.delete()
        messages.success(request, 'Invoice deleted successfully.')
    return redirect('invoices_list')

@login_required
def invoice_detail(request, id):
    return render(request, 'clinic/invoice_detail.html')

@login_required
def reports(request):
    return render(request, 'clinic/reports.html')

@login_required
def settings(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        try:
            # Update Full Name
            if full_name:
                name_parts = full_name.split(' ', 1)
                request.user.first_name = name_parts[0]
                request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Update Email
            if email:
                request.user.email = email
                
            request.user.save()
            messages.success(request, 'تم تحديث بيانات المستخدم بنجاح.')
            return redirect('settings')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء التحديث: {e}')
            
    return render(request, 'clinic/settings.html')

from django.core.exceptions import PermissionDenied

def doctor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'doctor':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

@login_required
@doctor_required
def users_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'clinic/users_list.html', {'users': users})

@login_required
@doctor_required
def edit_user(request, pk):
    try:
        user_to_edit = get_object_or_404(User, pk=pk)
        
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            role = request.POST.get('role')
            is_active = request.POST.get('is_active') == 'on'
            
            try:
                user_to_edit.first_name = first_name
                user_to_edit.last_name = last_name
                user_to_edit.email = email
                
                # Prevent changing own role/active status
                if request.user.pk != user_to_edit.pk:
                    user_to_edit.role = role
                    user_to_edit.is_active = is_active
                    
                user_to_edit.save()
                messages.success(request, 'تم تحديث بيانات المستخدم بنجاح.')
                return redirect('users_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء التحديث: {e}')
                
        return render(request, 'clinic/edit_user.html', {'user_obj': user_to_edit})
    except Exception as e:
        # Debugging: Print error to console and returned page
        print(f"DEBUG ERROR in edit_user: {e}")
        from django.http import HttpResponse
        return HttpResponse(f"Error: {e}")

@login_required
@doctor_required
def change_user_password(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        password = request.POST.get('password')
        if password:
            user_to_edit.set_password(password)
            user_to_edit.save()
            messages.success(request, f'تم تغيير كلمة المرور للمستخدم {user_to_edit.username} بنجاح.')
            return redirect('users_list')
        else:
            messages.error(request, 'يرجى إدخال كلمة المرور.')
            
    return render(request, 'clinic/change_password.html', {'user_obj': user_to_edit})

@login_required
@doctor_required
def delete_user(request, pk):
    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, pk=pk)
        
        # Prevent self deletion
        if user_to_delete.pk == request.user.pk:
            messages.error(request, 'لا يمكنك حذف حسابك الحالي.')
        else:
            user_name = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f'تم حذف المستخدم {user_name} بنجاح.')
            
    return redirect('users_list')

@login_required
@doctor_required
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'receptionist')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        errors = []
        
        if not username:
            errors.append('اسم المستخدم مطلوب.')
        elif User.objects.filter(username=username).exists():
            errors.append('اسم المستخدم موجود بالفعل.')
            
        if not password:
            errors.append('كلمة المرور مطلوبة.')
        elif password != confirm_password:
            errors.append('كلمة المرور وتأكيد كلمة المرور غير متطابقين.')
            
        if role not in ['doctor', 'receptionist']:
            errors.append('الدور الوظيفي غير صحيح.')
            
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'clinic/create_user.html', {
                'form_data': {
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': role,
                    'is_active': is_active,
                }
            })
        
        try:
            new_user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                is_active=is_active
            )
            new_user.set_password(password)
            new_user.save()
            
            messages.success(request, f'تم إنشاء المستخدم {username} بنجاح.')
            return redirect('users_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء المستخدم: {e}')
            
    return render(request, 'clinic/create_user.html')

def custom_404(request, exception):
    return render(request, 'clinic/404.html', status=404)

