from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
import csv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdminProfileForm, AppointmentForm, BillingForm, DepartmentForm, DoctorForm, HospitalSettingsForm, PatientForm, RegistrationForm, SettingsPasswordForm, UserSettingsForm
from .models import Appointment, Billing, Department, Doctor, HospitalSettings, Patient, UserSettings


def login_view(request):
    if request.user.is_authenticated:
        return redirect("patients:dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "patients:dashboard")
    return render(request, "registration/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("patients:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to MediCare Hospital.")
        return redirect("patients:dashboard")
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("patients:login")


def patient_list(request):
    query = request.GET.get("q", "").strip()
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(
            Q(patient_id__icontains=query)
            | Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(department__icontains=query)
            | Q(assigned_doctor__icontains=query)
        )
    context = {
        "patients": patients,
        "query": query,
        "total_patients": Patient.objects.count(),
        "new_today": Patient.objects.filter(admission_date=date.today()).count(),
        "admitted_count": Patient.objects.filter(status="Admitted").count(),
        "discharged_count": Patient.objects.filter(status="Discharged").count(),
    }
    return render(request, "patients/patient_list.html", context)


def dashboard(request):
    today = date.today()
    department_counts = list(
        Patient.objects.values("department").order_by("department").annotate(total=models.Count("id"))
    )
    department_counts.sort(key=lambda item: item["total"], reverse=True)
    department_counts = department_counts[:4]
    department_total = sum(item["total"] for item in department_counts)
    palette = ["blue", "teal", "purple", "orange"]
    department_stats = [
        {
            "name": item["department"],
            "total": item["total"],
            "percent": round(item["total"] * 100 / department_total) if department_total else 0,
            "color": palette[index],
        }
        for index, item in enumerate(department_counts)
    ]
    chart_segments = []
    chart_position = 0
    chart_colors = ["#15a4e4", "#14b7a5", "#914bea", "#ff9d00"]
    for index, item in enumerate(department_stats):
        next_position = chart_position + item["percent"]
        chart_segments.append(f"{chart_colors[index]} {chart_position}% {next_position}%")
        chart_position = next_position

    months = []
    admissions_by_month = defaultdict(int)
    for offset in range(5, -1, -1):
        month_index = today.year * 12 + today.month - 1 - offset
        month_year, month_number = divmod(month_index, 12)
        month_start = date(month_year, month_number + 1, 1)
        next_month_index = month_index + 1
        next_year, next_number = divmod(next_month_index, 12)
        next_month = date(next_year, next_number + 1, 1)
        month_name = month_start.strftime("%b")
        months.append(month_name)
        admissions_by_month[month_name] = Patient.objects.filter(
            admission_date__gte=month_start, admission_date__lt=next_month,
        ).count()
    max_admissions = max(admissions_by_month.values(), default=0) or 1
    chart_points = [max(12, round(admissions_by_month[month] * 120 / max_admissions)) for month in months]
    return render(request, "patients/dashboard.html", {
        "total_patients": Patient.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "today_appointments": Appointment.objects.filter(appointment_date=today).count(),
        "available_beds": 0,
        "department_stats": department_stats,
        "department_chart": ", ".join(chart_segments) if chart_segments else "#e7edf3 0 100%",
        "department_total": department_total,
        "months": months,
        "chart_points": chart_points,
        "recent_appointments": Appointment.objects.select_related("patient", "doctor").order_by("-appointment_date", "-appointment_time")[:4],
        "recent_patients": Patient.objects.order_by("-created_at")[:4],
        "today_schedule": Appointment.objects.select_related("patient", "doctor").filter(appointment_date=today).exclude(status="Cancelled")[:4],
        "total_revenue": Billing.objects.filter(payment_status="Paid").aggregate(total=models.Sum("total_amount"))["total"] or Decimal("0"),
        "pending_bills": Billing.objects.filter(payment_status__in=["Pending", "Partially Paid"]).count(),
        "activity_appointments": Appointment.objects.select_related("patient", "doctor").order_by("-created_at")[:3],
        "hospital_video_url": getattr(settings, "HOSPITAL_VIDEO_URL", ""),
    })


def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, "patients/patient_detail.html", {"patient": patient})


def patient_create(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save()
        messages.success(request, "Patient added successfully.")
        return redirect("patients:detail", pk=patient.pk)
    return render(request, "patients/patient_form.html", {"form": form, "page_title": "Add New Patient", "submit_label": "Add Patient"})


def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Patient details updated successfully.")
        return redirect("patients:detail", pk=patient.pk)
    return render(request, "patients/patient_form.html", {"form": form, "patient": patient, "page_title": "Edit Patient", "submit_label": "Save Changes"})


def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        patient.delete()
        messages.success(request, "Patient deleted successfully.")
        return redirect("patients:list")
    return render(request, "patients/patient_confirm_delete.html", {"patient": patient})


def doctor_list(request):
    query = request.GET.get("q", "").strip()
    doctors = Doctor.objects.all()
    if query:
        doctors = doctors.filter(
            Q(full_name__icontains=query)
            | Q(doctor_id__icontains=query)
            | Q(specialization__icontains=query)
            | Q(department__icontains=query)
            | Q(phone__icontains=query)
        )
    context = {
        "doctors": doctors,
        "query": query,
        "total_doctors": Doctor.objects.count(),
        "available_doctors": Doctor.objects.filter(availability_status="Available").count(),
        "on_leave_doctors": Doctor.objects.filter(availability_status="On Leave").count(),
        "departments_count": Doctor.objects.values("department").distinct().count(),
    }
    return render(request, "patients/doctor_list.html", context)


def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    return render(request, "patients/doctor_detail.html", {"doctor": doctor})


def doctor_create(request):
    form = DoctorForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save()
        messages.success(request, "Doctor added successfully.")
        return redirect("patients:doctor_detail", pk=doctor.pk)
    return render(request, "patients/doctor_form.html", {"form": form, "page_title": "Add New Doctor", "submit_label": "Add Doctor"})


def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, request.FILES or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor details updated successfully.")
        return redirect("patients:doctor_detail", pk=doctor.pk)
    return render(request, "patients/doctor_form.html", {"form": form, "doctor": doctor, "page_title": "Edit Doctor", "submit_label": "Save Changes"})


def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == "POST":
        doctor.delete()
        messages.success(request, "Doctor deleted successfully.")
        return redirect("patients:doctor_list")
    return render(request, "patients/doctor_confirm_delete.html", {"doctor": doctor})


def appointment_list(request):
    query = request.GET.get("q", "").strip()
    selected_date = request.GET.get("date", "").strip()
    selected_doctor = request.GET.get("doctor", "").strip()
    selected_department = request.GET.get("department", "").strip()
    selected_status = request.GET.get("status", "").strip()
    appointments = Appointment.objects.select_related("patient", "doctor").all()
    if query:
        appointments = appointments.filter(
            Q(appointment_id__icontains=query)
            | Q(patient__full_name__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(doctor__full_name__icontains=query)
        )
    if selected_date:
        appointments = appointments.filter(appointment_date=selected_date)
    if selected_doctor:
        appointments = appointments.filter(doctor_id=selected_doctor)
    if selected_department:
        appointments = appointments.filter(department=selected_department)
    if selected_status:
        appointments = appointments.filter(status=selected_status)
    paginator = Paginator(appointments, 4)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    today = date.today()
    context = {
        "appointments": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "selected_date": selected_date,
        "selected_doctor": selected_doctor,
        "selected_department": selected_department,
        "selected_status": selected_status,
        "total_appointments": Appointment.objects.count(),
        "today_appointments": Appointment.objects.filter(appointment_date=today).count(),
        "upcoming_appointments": Appointment.objects.filter(appointment_date__gte=today, status__in=["Scheduled", "Confirmed", "Pending"]).count(),
        "cancelled_appointments": Appointment.objects.filter(status="Cancelled").count(),
        "doctors": Doctor.objects.all(),
        "departments": Appointment.objects.values_list("department", flat=True).distinct().order_by("department"),
        "statuses": Appointment.STATUS_CHOICES,
        "today_schedule": Appointment.objects.select_related("patient", "doctor").filter(appointment_date=today).exclude(status="Cancelled")[:4],
    }
    return render(request, "patients/appointment_list.html", context)


def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment.objects.select_related("patient", "doctor"), pk=pk)
    return render(request, "patients/appointment_detail.html", {"appointment": appointment})


def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        appointment = form.save()
        messages.success(request, "Appointment booked successfully.")
        return redirect("patients:appointment_detail", pk=appointment.pk)
    return render(request, "patients/appointment_form.html", {"form": form, "page_title": "Book Appointment", "submit_label": "Book Appointment"})


def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Appointment updated successfully.")
        return redirect("patients:appointment_detail", pk=appointment.pk)
    return render(request, "patients/appointment_form.html", {"form": form, "appointment": appointment, "page_title": "Edit Appointment", "submit_label": "Save Changes"})


def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appointment.status = "Cancelled"
        appointment.save(update_fields=["status", "updated_at"])
        messages.success(request, "Appointment cancelled successfully.")
    return redirect("patients:appointment_detail", pk=appointment.pk)


def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect("patients:appointment_list")
    return render(request, "patients/appointment_confirm_delete.html", {"appointment": appointment})


def department_list(request):
    query = request.GET.get("q", "").strip()
    departments_query = Department.objects.select_related("head_doctor").all()
    if query:
        departments_query = departments_query.filter(
            Q(department_id__icontains=query)
            | Q(name__icontains=query)
            | Q(head_doctor__full_name__icontains=query)
        )
    departments = list(departments_query)
    for department in departments:
        department.doctors_total = Doctor.objects.filter(department=department.name).count()
        department.patients_total = Patient.objects.filter(department=department.name).count()
    page_obj = Paginator(departments, 4).get_page(request.GET.get("page", 1))
    return render(request, "patients/department_list.html", {
        "departments": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "total_departments": Department.objects.count(),
        "active_departments": Department.objects.filter(status="Active").count(),
        "total_doctors": Doctor.objects.count(),
        "total_patients": Patient.objects.count(),
    })


def department_detail(request, pk):
    department = get_object_or_404(Department.objects.select_related("head_doctor"), pk=pk)
    department.doctors_total = Doctor.objects.filter(department=department.name).count()
    department.patients_total = Patient.objects.filter(department=department.name).count()
    return render(request, "patients/department_detail.html", {"department": department})


def department_create(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        department = form.save()
        messages.success(request, "Department added successfully.")
        return redirect("patients:department_detail", pk=department.pk)
    return render(request, "patients/department_form.html", {"form": form, "page_title": "Add Department", "submit_label": "Add Department"})


def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department details updated successfully.")
        return redirect("patients:department_detail", pk=department.pk)
    return render(request, "patients/department_form.html", {"form": form, "department": department, "page_title": "Edit Department", "submit_label": "Save Changes"})


def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect("patients:department_list")
    return render(request, "patients/department_confirm_delete.html", {"department": department})


def billing_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    bill_date = request.GET.get("date", "").strip()
    department = request.GET.get("department", "").strip()
    bills = Billing.objects.select_related("patient", "doctor", "department").all()
    if query:
        bills = bills.filter(
            Q(bill_id__icontains=query)
            | Q(patient__full_name__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(doctor__full_name__icontains=query)
        )
    if status:
        bills = bills.filter(payment_status=status)
    if bill_date:
        bills = bills.filter(bill_date=bill_date)
    if department:
        bills = bills.filter(department_id=department)
    return render(request, "patients/billing_list.html", {
        "bills": Paginator(bills, 8).get_page(request.GET.get("page", 1)),
        "query": query,
        "selected_status": status,
        "selected_date": bill_date,
        "selected_department": department,
        "total_bills": Billing.objects.count(),
        "paid_bills": Billing.objects.filter(payment_status="Paid").count(),
        "pending_bills": Billing.objects.filter(payment_status__in=["Pending", "Partially Paid"]).count(),
        "total_revenue": sum(Billing.objects.filter(payment_status="Paid").values_list("total_amount", flat=True), Decimal("0")),
        "statuses": Billing.PAYMENT_STATUS_CHOICES,
        "departments": Department.objects.all(),
    })


def billing_create(request):
    form = BillingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        bill = form.save()
        messages.success(request, "Bill created successfully.")
        return redirect("patients:billing_detail", pk=bill.pk)
    return render(request, "patients/billing_form.html", {"form": form, "page_title": "Create New Bill", "submit_label": "Create Bill"})


def billing_detail(request, pk):
    bill = get_object_or_404(Billing.objects.select_related("patient", "doctor", "department"), pk=pk)
    return render(request, "patients/billing_detail.html", {"bill": bill})


def billing_update(request, pk):
    bill = get_object_or_404(Billing, pk=pk)
    form = BillingForm(request.POST or None, instance=bill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Bill updated successfully.")
        return redirect("patients:billing_detail", pk=bill.pk)
    return render(request, "patients/billing_form.html", {"form": form, "bill": bill, "page_title": "Edit Bill", "submit_label": "Save Changes"})


def billing_delete(request, pk):
    bill = get_object_or_404(Billing, pk=pk)
    if request.method == "POST":
        bill.delete()
        messages.success(request, "Bill deleted successfully.")
        return redirect("patients:billing_list")
    return render(request, "patients/billing_confirm_delete.html", {"bill": bill})


def reports(request):
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    department_id = request.GET.get("department", "").strip()
    doctor_id = request.GET.get("doctor", "").strip()
    report_type = request.GET.get("report_type", "overview").strip()
    start = end = None
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    except ValueError:
        start_date = end_date = ""

    patients = Patient.objects.all()
    appointments = Appointment.objects.select_related("patient", "doctor").all()
    bills = Billing.objects.select_related("patient", "doctor", "department").all()
    if start:
        patients = patients.filter(admission_date__gte=start)
        appointments = appointments.filter(appointment_date__gte=start)
        bills = bills.filter(bill_date__gte=start)
    if end:
        patients = patients.filter(admission_date__lte=end)
        appointments = appointments.filter(appointment_date__lte=end)
        bills = bills.filter(bill_date__lte=end)
    if department_id:
        department = Department.objects.filter(pk=department_id).first()
        if department:
            patients = patients.filter(department=department.name)
            appointments = appointments.filter(department=department.name)
            bills = bills.filter(department_id=department.pk)
    if doctor_id:
        patients = patients.filter(assigned_doctor__icontains=Doctor.objects.filter(pk=doctor_id).values_list("full_name", flat=True).first() or "\0")
        appointments = appointments.filter(doctor_id=doctor_id)
        bills = bills.filter(doctor_id=doctor_id)

    patient_status = list(patients.values("status").annotate(total=models.Count("id")))
    appointment_departments = list(appointments.values("department").annotate(total=models.Count("id")).order_by("-total"))
    doctor_stats = list(appointments.values("doctor__full_name").annotate(total=models.Count("id")).order_by("-total")[:8])
    revenue_by_department = list(bills.filter(payment_status="Paid").values("department__name").annotate(total=models.Sum("total_amount")).order_by("-total"))
    registration_by_month = list(patients.values("admission_date").annotate(total=models.Count("id")).order_by("admission_date"))
    revenue_total = bills.filter(payment_status="Paid").aggregate(total=models.Sum("total_amount"))["total"] or Decimal("0")
    context = {
        "total_patients": patients.count(),
        "total_doctors": Doctor.objects.filter(pk=doctor_id).count() if doctor_id else Doctor.objects.count(),
        "total_appointments": appointments.count(),
        "total_revenue": revenue_total,
        "patient_status": patient_status,
        "appointment_departments": appointment_departments,
        "doctor_stats": doctor_stats,
        "revenue_by_department": revenue_by_department,
        "registration_by_month": registration_by_month,
        "patients_report": patients.order_by("-admission_date")[:10],
        "doctors_report": Doctor.objects.filter(pk=doctor_id) if doctor_id else Doctor.objects.all()[:10],
        "appointments_report": appointments.order_by("-appointment_date", "-appointment_time")[:10],
        "departments_report": Department.objects.all()[:10],
        "billing_report": bills.order_by("-bill_date")[:10],
        "departments": Department.objects.all(),
        "doctors": Doctor.objects.all(),
        "selected_start": start_date,
        "selected_end": end_date,
        "selected_department": department_id,
        "selected_doctor": doctor_id,
        "selected_report_type": report_type,
    }
    return render(request, "patients/reports.html", context)


def reports_export(request):
    report_type = request.GET.get("report_type", "overview")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    appointments = Appointment.objects.select_related("patient", "doctor").all()
    bills = Billing.objects.select_related("patient", "department").all()
    if start_date:
        appointments = appointments.filter(appointment_date__gte=start_date)
        bills = bills.filter(bill_date__gte=start_date)
    if end_date:
        appointments = appointments.filter(appointment_date__lte=end_date)
        bills = bills.filter(bill_date__lte=end_date)
    if request.GET.get("department"):
        appointments = appointments.filter(department=Department.objects.filter(pk=request.GET["department"]).values_list("name", flat=True).first())
        bills = bills.filter(department_id=request.GET["department"])
    if request.GET.get("doctor"):
        appointments = appointments.filter(doctor_id=request.GET["doctor"])
        bills = bills.filter(doctor_id=request.GET["doctor"])
    rows = appointments[:100] if report_type == "appointments" else bills[:100]
    output = []
    if report_type == "appointments":
        output.append(["Appointment ID", "Patient", "Doctor", "Department", "Date", "Status"])
        output.extend([item.appointment_id, item.patient.full_name, item.doctor.full_name, item.department, item.appointment_date, item.status] for item in rows)
    else:
        output.append(["Bill ID", "Patient", "Department", "Bill Date", "Total Amount", "Payment Status"])
        output.extend([item.bill_id, item.patient.full_name, item.department.name if item.department else "", item.bill_date, item.total_amount, item.payment_status] for item in rows)
    csv_response = HttpResponse(content_type="text/csv")
    csv_response["Content-Disposition"] = f'attachment; filename="{report_type}-report.csv"'
    writer = csv.writer(csv_response)
    writer.writerows(output)
    return csv_response


def settings_page(request):
    hospital_settings = HospitalSettings.objects.first() or HospitalSettings.objects.create()
    if request.user.is_authenticated:
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        profile_form = AdminProfileForm(request.POST or None, instance=request.user, prefix="profile")
        profile_form.fields["phone"].initial = user_settings.phone
        preferences_form = UserSettingsForm(request.POST or None, instance=user_settings, prefix="preferences")
        password_form = SettingsPasswordForm(request.user, request.POST or None, prefix="password")
    else:
        profile_form = AdminProfileForm(prefix="profile")
        preferences_form = UserSettingsForm(prefix="preferences")
        password_form = None
    hospital_form = HospitalSettingsForm(request.POST or None, instance=hospital_settings, prefix="hospital")
    if request.method == "POST":
        action = request.POST.get("settings_action")
        if action == "hospital" and hospital_form.is_valid():
            hospital_form.save()
            messages.success(request, "Hospital profile updated successfully.")
        elif action == "profile" and request.user.is_authenticated and profile_form.is_valid():
            profile_form.save()
            user_settings.phone = profile_form.cleaned_data["phone"]
            user_settings.save(update_fields=["phone"])
            messages.success(request, "Admin profile updated successfully.")
        elif action == "preferences" and request.user.is_authenticated and preferences_form.is_valid():
            preferences_form.save()
            messages.success(request, "Notification and system preferences updated.")
        elif action == "password" and password_form and password_form.is_valid():
            password_form.save()
            messages.success(request, "Password changed successfully.")
        elif action in {"profile", "preferences", "password"} and not request.user.is_authenticated:
            messages.error(request, "Log in to update admin profile, preferences, or password settings.")
        return redirect("patients:settings")
    return render(request, "patients/settings.html", {
        "hospital_form": hospital_form, "profile_form": profile_form,
        "preferences_form": preferences_form, "password_form": password_form,
        "settings_user": request.user if request.user.is_authenticated else None,
    })
