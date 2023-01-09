# Generated by Django 4.1.4 on 2023-01-09 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aqg", "0005_alter_question_paragraph"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dataset",
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
                ("name", models.CharField(max_length=40, unique=True)),
                ("comment", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
