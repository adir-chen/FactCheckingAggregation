# Generated by Django 2.1.3 on 2018-12-25 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0003_auto_20181220_1829'),
    ]

    operations = [
        migrations.RenameField(
            model_name='claim',
            old_name='title',
            new_name='claim',
        ),
    ]