# Generated by Django 5.0.6 on 2024-06-13 09:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0002_scrapeditem_alter_todoitem_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Club",
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
                ("name", models.CharField(max_length=220)),
                ("money", models.IntegerField()),
            ],
        ),
    ]
