from datetime import date

from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    STATUS_CHOICES = [("Admitted", "Admitted"), ("Discharged", "Discharged"), ("Outpatient", "Outpatient")]
    BLOOD_GROUP_CHOICES = [(group, group) for group in ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")]

    patient_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=120)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=80)
    assigned_doctor = models.CharField(max_length=120)
    admission_date = models.DateField()
    medical_history = models.TextField(blank=True)
    allergies = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Admitted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.patient_id})"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Doctor(models.Model):
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    AVAILABILITY_CHOICES = [("Available", "Available"), ("Busy", "Busy"), ("On Leave", "On Leave")]

    doctor_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=120)
    profile_photo = models.ImageField(upload_to="doctors/", blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.TextField()
    specialization = models.CharField(max_length=100)
    department = models.CharField(max_length=80)
    qualification = models.CharField(max_length=150)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_days = models.CharField(max_length=120)
    available_time = models.CharField(max_length=80)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default="Available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.doctor_id})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Scheduled", "Scheduled"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("Pending", "Pending"),
    ]

    appointment_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    department = models.CharField(max_length=80)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Scheduled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "appointment_date", "appointment_time"],
                name="unique_doctor_appointment_slot",
            ),
        ]

    def __str__(self):
        return f"{self.appointment_id} - {self.patient.full_name}"


class Department(models.Model):
    STATUS_CHOICES = [("Active", "Active"), ("Inactive", "Inactive")]

    department_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, unique=True)
    head_doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name="headed_departments",
    )
    contact_extension = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.department_id})"


class Billing(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Partially Paid", "Partially Paid"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("Bank Transfer", "Bank Transfer"),
        ("Insurance", "Insurance"),
    ]

    bill_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="bills")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="bills")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="bills")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_test_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="Cash")
    bill_date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-bill_date", "-created_at"]

    def calculate_total(self):
        charges = sum((self.consultation_fee, self.room_charges, self.medicine_charges, self.lab_test_charges, self.other_charges))
        return max(charges - self.discount + self.tax, 0)

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill_id} - {self.patient.full_name}"


class HospitalSettings(models.Model):
    hospital_name = models.CharField(max_length=150, default="MediCare Hospital")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hospital_name


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    phone = models.CharField(max_length=30, blank=True)
    appointment_notifications = models.BooleanField(default=True)
    patient_notifications = models.BooleanField(default=True)
    billing_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    date_format = models.CharField(max_length=20, default="MMM DD, YYYY")
    time_format = models.CharField(max_length=10, default="12-hour")
    language = models.CharField(max_length=30, default="English")
    theme = models.CharField(max_length=20, default="Light")

    def __str__(self):
        return f"Settings for {self.user.username}"
