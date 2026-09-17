from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login_page"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("patients/", views.patient_list, name="list"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("patients/<int:pk>/", views.patient_detail, name="detail"),
    path("patients/add/", views.patient_create, name="create"),
    path("patients/<int:pk>/edit/", views.patient_update, name="update"),
    path("patients/<int:pk>/delete/", views.patient_delete, name="delete"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/add/", views.doctor_create, name="doctor_create"),
    path("doctors/<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("doctors/<int:pk>/edit/", views.doctor_update, name="doctor_update"),
    path("doctors/<int:pk>/delete/", views.doctor_delete, name="doctor_delete"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/add/", views.appointment_create, name="appointment_create"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="appointment_update"),
    path("appointments/<int:pk>/cancel/", views.appointment_cancel, name="appointment_cancel"),
    path("appointments/<int:pk>/delete/", views.appointment_delete, name="appointment_delete"),
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_create, name="department_create"),
    path("departments/<int:pk>/", views.department_detail, name="department_detail"),
    path("departments/<int:pk>/edit/", views.department_update, name="department_update"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),
    path("billing/", views.billing_list, name="billing_list"),
    path("billing/add/", views.billing_create, name="billing_create"),
    path("billing/<int:pk>/", views.billing_detail, name="billing_detail"),
    path("billing/<int:pk>/edit/", views.billing_update, name="billing_update"),
    path("billing/<int:pk>/delete/", views.billing_delete, name="billing_delete"),
    path("reports/", views.reports, name="reports"),
    path("reports/export/", views.reports_export, name="reports_export"),
    path("settings/", views.settings_page, name="settings"),
]
