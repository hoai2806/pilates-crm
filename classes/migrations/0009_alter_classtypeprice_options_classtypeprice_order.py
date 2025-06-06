# Generated by Django 4.2.21 on 2025-05-23 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0008_alter_classtypeprice_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='classtypeprice',
            options={'ordering': ['order', 'class_format', 'number_of_sessions'], 'verbose_name': 'Bảng giá lớp học', 'verbose_name_plural': 'Bảng giá lớp học'},
        ),
        migrations.AddField(
            model_name='classtypeprice',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Thứ tự'),
        ),
    ]
