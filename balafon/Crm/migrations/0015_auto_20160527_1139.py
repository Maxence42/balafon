# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0014_mailprovider_port'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mail_import',
            name='password',
        ),
        migrations.AddField(
            model_name='mail_import',
            name='date',
            field=models.DateField(default=None, verbose_name='date'),
        ),
    ]
