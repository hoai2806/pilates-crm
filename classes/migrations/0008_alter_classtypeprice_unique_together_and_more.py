# Generated by Django 4.2.21 on 2025-05-23 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0007_attendance_customer_package_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='classtypeprice',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='classtypeprice',
            name='time_slot',
            field=models.CharField(choices=[('ALL', 'Tất cả khung giờ'), ('MORNING_LOW', 'Thấp điểm sáng'), ('MORNING_MID', 'Trung điểm sáng'), ('MORNING_PEAK', 'Cao điểm sáng'), ('AFTERNOON_LOW', 'Thấp điểm chiều'), ('AFTERNOON_MID', 'Trung điểm chiều'), ('AFTERNOON_PEAK', 'Cao điểm chiều')], default='ALL', max_length=20, verbose_name='Khung giờ'),
        ),
        migrations.AlterField(
            model_name='classtypeprice',
            name='class_format',
            field=models.CharField(choices=[('PT', 'PT 1:1'), ('GROUP_2', 'Nhóm 1:2'), ('GROUP_3', 'Nhóm 1:3'), ('GROUP_6', 'Nhóm 1:6')], max_length=20, verbose_name='Hình thức lớp'),
        ),
        migrations.AlterUniqueTogether(
            name='classtypeprice',
            unique_together={('class_type', 'class_format', 'time_slot', 'number_of_sessions')},
        ),
    ]
