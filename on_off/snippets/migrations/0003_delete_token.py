# Generated by Django 4.1 on 2023-06-07 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0002_query_token_delete_snippet"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Token",
        ),
    ]