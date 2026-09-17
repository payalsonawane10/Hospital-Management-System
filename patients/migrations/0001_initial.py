from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("patient_id", models.CharField(max_length=20, unique=True)),
                ("full_name", models.CharField(max_length=120)),
                ("date_of_birth", models.DateField()),
                ("gender", models.CharField(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], max_length=10)),
                ("phone", models.CharField(max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.TextField(blank=True)),
                ("blood_group", models.CharField(blank=True, choices=[("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"), ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")], max_length=3)),
                ("emergency_contact", models.CharField(blank=True, max_length=120)),
                ("department", models.CharField(max_length=80)),
                ("assigned_doctor", models.CharField(max_length=120)),
                ("admission_date", models.DateField()),
                ("medical_history", models.TextField(blank=True)),
                ("allergies", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("Admitted", "Admitted"), ("Discharged", "Discharged"), ("Outpatient", "Outpatient")], default="Admitted", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["full_name"]},
        ),
    ]
