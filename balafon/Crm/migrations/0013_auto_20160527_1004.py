# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0012_auto_20160518_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mail_Import',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mail_address', models.EmailField(max_length=200, verbose_name='Email address')),
                ('password', models.CharField(max_length=100, verbose_name='Password')),
            ],
        ),
        migrations.CreateModel(
            name='MailProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('imapServer', models.CharField(max_length=100, verbose_name='imap server')),
            ],
        ),
        migrations.AddField(
            model_name='mail_import',
            name='provider',
            field=models.ForeignKey(to='Crm.MailProvider'),
        ),
    ]
