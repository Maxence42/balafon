# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Crm', '0015_auto_20160527_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail_import',
            name='imported_by',
            field=models.ForeignKey(default=None, verbose_name='imported by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mail_import',
            name='date',
            field=models.DateField(default=None, verbose_name='Date'),
        ),
    ]
