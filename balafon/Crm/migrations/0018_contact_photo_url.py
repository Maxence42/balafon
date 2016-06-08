# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0017_mail_import_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='photo_url',
            field=models.CharField(max_length=300, null=True, verbose_name='photo url'),
        ),
    ]
