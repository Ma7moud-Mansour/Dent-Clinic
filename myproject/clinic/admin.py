from django.contrib import admin

# Register your models here.
from .models import User, Patient, Appointment, Visit, Payment

admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Visit)
admin.site.register(Payment)
