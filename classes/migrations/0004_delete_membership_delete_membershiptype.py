# Generated by Django 4.2.21 on 2025-05-19 02:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0003_alter_classtypeprice_class_format'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Membership',
        ),
        migrations.DeleteModel(
            name='MembershipType',
        ),
    ]
