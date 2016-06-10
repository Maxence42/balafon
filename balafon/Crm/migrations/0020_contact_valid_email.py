# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0019_error_mailaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='valid_email',
            field=models.BooleanField(default=True, verbose_name='valid email address'),
        ),
    ]
