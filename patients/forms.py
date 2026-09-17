from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from .models import Appointment, Billing, Department, Doctor, HospitalSettings, Patient, UserSettings


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "patient_id", "full_name", "date_of_birth", "gender", "phone", "email",
            "address", "blood_group", "emergency_contact", "department", "assigned_doctor",
            "admission_date", "medical_history", "allergies", "status",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "admission_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "medical_history": forms.Textarea(attrs={"rows": 3}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "doctor_id", "full_name", "profile_photo", "gender", "date_of_birth", "phone", "email",
            "address", "specialization", "department", "qualification", "experience", "consultation_fee",
            "available_days", "available_time", "availability_status",
        ]
        labels = {
            "doctor_id": "Doctor ID",
            "full_name": "Doctor Name",
            "profile_photo": "Profile Photo",
            "date_of_birth": "Date of Birth",
            "consultation_fee": "Consultation Fee",
            "available_days": "Available Days",
            "available_time": "Available Time",
            "availability_status": "Availability Status",
        }
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "experience": forms.NumberInput(attrs={"min": 0}),
            "consultation_fee": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "appointment_id", "patient", "doctor", "department", "appointment_date", "appointment_time",
            "reason", "notes", "status",
        ]
        labels = {
            "appointment_id": "Appointment ID",
            "appointment_date": "Appointment Date",
            "appointment_time": "Appointment Time",
        }
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")
        doctor = cleaned_data.get("doctor")
        if not self.instance.pk and appointment_date and appointment_date < date.today():
            self.add_error("appointment_date", "New appointments cannot be booked in the past.")
        if doctor and appointment_date and appointment_time:
            duplicate = Appointment.objects.filter(
                doctor=doctor, appointment_date=appointment_date, appointment_time=appointment_time,
            ).exclude(pk=self.instance.pk)
            if duplicate.exists():
                self.add_error("appointment_time", "This doctor already has an appointment at that time.")
        return cleaned_data


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["department_id", "name", "head_doctor", "contact_extension", "status"]
        labels = {
            "department_id": "Department ID",
            "name": "Department Name",
            "head_doctor": "Head Doctor",
            "contact_extension": "Contact / Extension",
        }


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = [
            "bill_id", "patient", "doctor", "department", "consultation_fee", "room_charges",
            "medicine_charges", "lab_test_charges", "other_charges", "discount", "tax",
            "payment_status", "payment_method", "bill_date",
        ]
        labels = {
            "bill_id": "Bill ID",
            "lab_test_charges": "Lab / Test Charges",
            "bill_date": "Bill Date",
            "payment_status": "Payment Status",
            "payment_method": "Payment Method",
        }
        widgets = {
            "bill_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("consultation_fee", "room_charges", "medicine_charges", "lab_test_charges", "other_charges", "discount", "tax"):
            self.fields[name].widget = forms.NumberInput(attrs={"min": 0, "step": "0.01"})


class HospitalSettingsForm(forms.ModelForm):
    class Meta:
        model = HospitalSettings
        fields = ["hospital_name", "address", "phone", "email", "description"]
        labels = {"hospital_name": "Hospital Name", "address": "Hospital Address", "phone": "Phone Number", "description": "Hospital Description"}
        widgets = {"address": forms.Textarea(attrs={"rows": 3}), "description": forms.Textarea(attrs={"rows": 3})}


class AdminProfileForm(forms.ModelForm):
    full_name = forms.CharField(label="Full Name")

    class Meta:
        model = User
        fields = ["full_name", "email"]
        labels = {"email": "Email"}

    phone = forms.CharField(required=False, label="Phone Number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["full_name"].initial = self.instance.get_full_name() or self.instance.username

    def save(self, commit=True):
        user = super().save(commit=False)
        parts = self.cleaned_data["full_name"].strip().split(maxsplit=1)
        user.first_name = parts[0] if parts else ""
        user.last_name = parts[1] if len(parts) > 1 else ""
        if commit:
            user.save()
        return user


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ["appointment_notifications", "patient_notifications", "billing_notifications", "email_notifications", "date_format", "time_format", "language", "theme"]
        widgets = {
            "appointment_notifications": forms.CheckboxInput(), "patient_notifications": forms.CheckboxInput(),
            "billing_notifications": forms.CheckboxInput(), "email_notifications": forms.CheckboxInput(),
        }


class SettingsPasswordForm(PasswordChangeForm):
    pass


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label="Full Name")

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "password1", "password2"]
