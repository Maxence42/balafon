# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0018_contact_photo_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error_MailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=200, verbose_name='Email address')),
                ('date', models.CharField(max_length=200, verbose_name='Sending date')),
                ('error', models.CharField(max_length=200, verbose_name='Error')),
            ],
        ),
    ]
