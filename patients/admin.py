from django.contrib import admin

from .models import Appointment, Billing, Department, Doctor, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "full_name", "department", "assigned_doctor", "status")
    search_fields = ("patient_id", "full_name", "phone", "email")
    list_filter = ("status", "gender", "department")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("doctor_id", "full_name", "specialization", "department", "availability_status")
    search_fields = ("doctor_id", "full_name", "specialization", "department", "phone")
    list_filter = ("availability_status", "gender", "department")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("appointment_id", "patient", "doctor", "appointment_date", "appointment_time", "status")
    search_fields = ("appointment_id", "patient__full_name", "patient__patient_id", "doctor__full_name")
    list_filter = ("appointment_date", "department", "status")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("department_id", "name", "head_doctor", "contact_extension", "status")
    search_fields = ("department_id", "name", "head_doctor__full_name")
    list_filter = ("status",)


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ("bill_id", "patient", "doctor", "total_amount", "payment_status", "bill_date")
    search_fields = ("bill_id", "patient__full_name", "patient__patient_id", "doctor__full_name")
    list_filter = ("payment_status", "payment_method", "bill_date", "department")
