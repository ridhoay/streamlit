# Generated by Django 5.0.6 on 2024-06-15 06:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_club"),
    ]

    operations = [
        migrations.CreateModel(
            name="PriceTrackerUsers",
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
                ("name", models.CharField(max_length=30)),
                ("email", models.EmailField(max_length=254, verbose_name="User Email")),
            ],
        ),
        migrations.AddField(
            model_name="scrapeditem",
            name="owner",
            field=models.ManyToManyField(blank=True, to="myapp.pricetrackerusers"),
        ),
    ]
