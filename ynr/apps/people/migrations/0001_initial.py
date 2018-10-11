# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-20 11:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import people.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("popolo", "0021_auto_20180918_1534"),
    ]

    operations = [
        migrations.CreateModel(
            name="PersonImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        max_length=512,
                        upload_to=people.models.person_image_path,
                    ),
                ),
                ("source", models.CharField(max_length=400)),
                (
                    "copyright",
                    models.CharField(
                        blank=True, default="other", max_length=64
                    ),
                ),
                ("user_notes", models.TextField(blank=True)),
                ("md5sum", models.CharField(blank=True, max_length=32)),
                (
                    "user_copyright",
                    models.CharField(blank=True, max_length=128),
                ),
                ("notes", models.TextField(blank=True)),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="popolo.Person",
                    ),
                ),
                (
                    "uploading_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]