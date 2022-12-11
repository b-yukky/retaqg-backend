# Generated by Django 4.1.4 on 2022-12-08 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("aqg", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="distractor",
            name="model",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="aqg.model"
            ),
        ),
        migrations.AddField(
            model_name="paragraph",
            name="document_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="paragraph",
            name="topic",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="question",
            name="status",
            field=models.CharField(
                choices=[("TE", "TEST"), ("EV", "EVALUATION"), ("PR", "PRODUCTION")],
                default="TS",
                max_length=2,
            ),
        ),
        migrations.CreateModel(
            name="Profile",
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
                ("english_validation", models.BooleanField(default=False)),
                ("english_false_answers", models.IntegerField(default=0)),
                ("english_proficiency", models.IntegerField(default=0)),
                ("is_student", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Evaluation",
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
                ("relevance", models.IntegerField()),
                ("acceptability", models.BooleanField()),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="aqg.question"
                    ),
                ),
            ],
        ),
    ]