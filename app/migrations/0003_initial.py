# Generated by Django 5.1.5 on 2025-03-03 15:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("app", "0002_delete_customuser"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExamSubmission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=100)),
                (
                    "exam_type",
                    models.CharField(
                        choices=[("CAT1", "CAT 1"), ("CAT2", "CAT 2")], max_length=10
                    ),
                ),
                (
                    "year",
                    models.CharField(
                        choices=[
                            ("1", "First Year"),
                            ("2", "Second Year"),
                            ("3", "Third Year"),
                            ("4", "Fourth Year"),
                        ],
                        max_length=1,
                    ),
                ),
                ("staff_name", models.CharField(max_length=100)),
                ("is_graded", models.BooleanField(default=False)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
