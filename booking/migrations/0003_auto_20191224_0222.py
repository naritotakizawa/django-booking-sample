# Generated by Django 2.2.9 on 2019-12-23 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_auto_20191221_1336'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='schedule',
            constraint=models.UniqueConstraint(fields=('start', 'end', 'staff'), name='unique_data'),
        ),
    ]