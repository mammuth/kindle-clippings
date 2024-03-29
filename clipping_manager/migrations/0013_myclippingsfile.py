# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-07-27 07:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clipping_manager', '0012_data_generate_clipping_hashs'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyClippingsFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Content')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Upload datetime')),
                ('language_header', models.CharField(blank=True, max_length=255, null=True, verbose_name='Accept-Language header')),
            ],
            options={
                'verbose_name': 'MyClippings file',
                'verbose_name_plural': 'MyClippings files',
            },
        ),
    ]
