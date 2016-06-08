# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Search', '0003_auto_20160531_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchresult',
            name='results',
            field=models.CharField(max_length=100000, verbose_name='ID list of results'),
        ),
    ]
