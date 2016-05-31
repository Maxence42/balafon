# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0016_auto_20160527_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail_import',
            name='content',
            field=models.CharField(default=b'', max_length=10000, verbose_name='Content'),
        ),
    ]
