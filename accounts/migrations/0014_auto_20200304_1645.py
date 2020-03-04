# Generated by Django 2.1.15 on 2020-03-04 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20200303_1653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leave',
            name='paid_days',
        ),
        migrations.AddField(
            model_name='leave',
            name='Planned_leave',
            field=models.PositiveIntegerField(blank=True, default=7, null=True, verbose_name='Paid Leave days per year counter'),
        ),
        migrations.AlterField(
            model_name='leave',
            name='casual_days',
            field=models.PositiveIntegerField(blank=True, default=7, null=True, verbose_name='Casual Leave days per year counter'),
        ),
        migrations.AlterField(
            model_name='leave',
            name='leavetype',
            field=models.CharField(choices=[('sick', 'Sick_Leave'), ('casual', 'Casual_Leave'), ('planned', 'Planned_leave'), ('study', 'Study_Leave')], default='sick', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='leave',
            name='sick_days',
            field=models.PositiveIntegerField(blank=True, default=7, null=True, verbose_name='Sick Leave days per year counter'),
        ),
    ]