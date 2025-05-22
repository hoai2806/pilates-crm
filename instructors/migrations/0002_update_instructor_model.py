from django.db import migrations, models

def combine_names(apps, schema_editor):
    Instructor = apps.get_model('instructors', 'Instructor')
    for instructor in Instructor.objects.all():
        instructor.full_name = f"{instructor.last_name} {instructor.first_name}"
        instructor.weekday_hourly_rate = instructor.hourly_rate
        instructor.sunday_hourly_rate = instructor.hourly_rate * 1.5
        instructor.save()

def reverse_combine_names(apps, schema_editor):
    Instructor = apps.get_model('instructors', 'Instructor')
    for instructor in Instructor.objects.all():
        name_parts = instructor.full_name.rsplit(' ', 1)
        if len(name_parts) > 1:
            instructor.last_name = name_parts[0]
            instructor.first_name = name_parts[1]
        else:
            instructor.last_name = ""
            instructor.first_name = name_parts[0]
        instructor.hourly_rate = instructor.weekday_hourly_rate
        instructor.save()

class Migration(migrations.Migration):

    dependencies = [
        ('instructors', '0001_initial'),
    ]

    operations = [
        # Thêm các trường mới
        migrations.AddField(
            model_name='instructor',
            name='full_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Họ và tên'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='weekday_hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Mức lương theo giờ (Thứ 2-7)'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='sunday_hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Mức lương theo giờ (Chủ nhật)'),
        ),
        
        # Điền dữ liệu vào các trường mới
        migrations.RunPython(combine_names, reverse_combine_names),
        
        # Làm cho các trường mới trở thành bắt buộc
        migrations.AlterField(
            model_name='instructor',
            name='full_name',
            field=models.CharField(max_length=100, verbose_name='Họ và tên'),
        ),
        migrations.AlterField(
            model_name='instructor',
            name='weekday_hourly_rate',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Mức lương theo giờ (Thứ 2-7)'),
        ),
        migrations.AlterField(
            model_name='instructor',
            name='sunday_hourly_rate',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Mức lương theo giờ (Chủ nhật)'),
        ),
        
        # Xóa các trường cũ
        migrations.RemoveField(
            model_name='instructor',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='instructor',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='instructor',
            name='hourly_rate',
        ),
        
        # Cập nhật ordering
        migrations.AlterModelOptions(
            name='instructor',
            options={'ordering': ['full_name'], 'verbose_name': 'Huấn luyện viên', 'verbose_name_plural': 'Huấn luyện viên'},
        ),
    ] 