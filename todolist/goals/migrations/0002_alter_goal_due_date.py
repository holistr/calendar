# Generated by Django 4.0.1 on 2023-01-11 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата выполнения'),
        ),
    ]