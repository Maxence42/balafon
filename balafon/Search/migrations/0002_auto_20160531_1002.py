# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Search', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nb_results', models.IntegerField(verbose_name='Number of results')),
                ('results', models.CharField(max_length=500, verbose_name='ID list of results')),
            ],
            options={
                'verbose_name': 'search result',
                'verbose_name_plural': 'search results',
            },
        ),
        migrations.AlterModelOptions(
            name='searchfield',
            options={'verbose_name': 'search field', 'verbose_name_plural': 'search fields'},
        ),
    ]
