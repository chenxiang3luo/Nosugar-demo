# Generated by Django 4.1 on 2023-06-14 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0005_remove_query_query_date_remove_query_user_task_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="finish_cnt",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="task",
            name="total_cnt",
            field=models.IntegerField(default=1),
        ),
    ]
