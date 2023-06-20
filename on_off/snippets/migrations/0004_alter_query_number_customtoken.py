# Generated by Django 4.1 on 2023-06-09 09:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("snippets", "0003_delete_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="query",
            name="number",
            field=models.CharField(max_length=11),
        ),
        migrations.CreateModel(
            name="CustomToken",
            fields=[
                (
                    "key",
                    models.CharField(max_length=40, primary_key=True, serialize=False),
                ),
                ("created", models.DateTimeField()),
                ("expires", models.DateTimeField()),
                ("count", models.IntegerField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custom_token",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]