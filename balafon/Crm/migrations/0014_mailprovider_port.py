# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0013_auto_20160527_1004'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailprovider',
            name='port',
            field=models.IntegerField(default=993, verbose_name='imap port'),
        ),
    ]
