# Generated by Django 4.2.21 on 2025-05-18 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('instructors', '0002_update_instructor_model'),
        ('customers', '0007_healthdocument_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateTimeField(verbose_name='Ngày giờ hẹn')),
                ('content', models.TextField(verbose_name='Nội dung cuộc hẹn')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='customers.customer', verbose_name='Khách hàng')),
                ('instructors', models.ManyToManyField(related_name='appointments', to='instructors.instructor', verbose_name='Huấn luyện viên')),
            ],
            options={
                'verbose_name': 'Cuộc hẹn',
                'verbose_name_plural': 'Cuộc hẹn',
                'ordering': ['-appointment_date'],
            },
        ),
    ]
