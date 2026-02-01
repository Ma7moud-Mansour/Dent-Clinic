from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_full_name() or self.username

class Patient(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.patient.full_name} - {self.date} {self.time}"

class Visit(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'doctor'},
        related_name='visits'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visit'
    )
    visit_date = models.DateField()
    description = models.TextField()
    notes = models.TextField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='created_visits'
    )


    def __str__(self):
        return f"Visit - {self.patient.full_name} ({self.visit_date})"

    @property
    def total_paid(self):
        return sum(payment.paid_amount for payment in self.payments.all())

    @property
    def remaining_amount(self):
        return self.total_cost - self.total_paid

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('visa', 'Visa'),
    )

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='created_payments'
    )


    def __str__(self):
        return f"{self.paid_amount} - {self.payment_method}"

class DentalXRay(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='xrays'
    )
    image = models.ImageField(upload_to='xrays/')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"X-Ray for {self.patient.full_name} ({self.created_at.date()})"

class ClinicSchedule(models.Model):
    """
    Singleton model for clinic working hours and scheduling configuration.
    Only ONE row should exist - use get_schedule() class method.
    """
    
    # Working days stored as JSON array of weekday integers
    # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    working_days = models.JSONField(
        default=list,
        help_text="List of working days (0=Mon, 1=Tue, ..., 6=Sun)"
    )
    
    start_time = models.TimeField(
        help_text="Clinic opening time"
    )
    
    end_time = models.TimeField(
        help_text="Clinic closing time"
    )
    
    slot_duration = models.PositiveIntegerField(
        default=30,
        help_text="Appointment slot duration in minutes"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedule_updates'
    )
    
    class Meta:
        verbose_name = "Clinic Schedule"
        verbose_name_plural = "Clinic Schedule"
    
    def __str__(self):
        return f"Clinic Schedule ({self.start_time} - {self.end_time})"
    
    @classmethod
    def get_schedule(cls):
        """
        Get the single clinic schedule instance.
        Creates a default one if none exists.
        """
        from datetime import time
        
        schedule = cls.objects.first()
        if not schedule:
            # Create default schedule
            schedule = cls.objects.create(
                working_days=[0, 1, 2, 3, 6],  # Sun-Thu (0=Mon, 6=Sun)
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration=30
            )
        return schedule
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and ClinicSchedule.objects.exists():
            existing = ClinicSchedule.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
