from django.core.management.base import BaseCommand
from instructors.models import Instructor
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Tạo dữ liệu giả lập cho huấn luyện viên'

    def handle(self, *args, **kwargs):
        instructors_data = [
            {
                'full_name': 'Nguyễn Văn A',
                'phone': '0987654321',
                'address': '123 Đường ABC, Quận 1, TP.HCM',
                'date_of_birth': date(1990, 1, 1),
                'gender': 'M',
                'bio': 'Huấn luyện viên có 5 năm kinh nghiệm trong lĩnh vực Pilates',
                'certifications': 'Chứng chỉ Pilates Matwork\nChứng chỉ Pilates Reformer',
                'specialties': 'Pilates, Yoga, Thể dục nhịp điệu',
                'hire_date': date(2023, 1, 1),
                'weekday_hourly_rate': 300000,
                'sunday_hourly_rate': 450000,
                'active': True
            },
            {
                'full_name': 'Trần Thị B',
                'phone': '0987654322',
                'address': '456 Đường XYZ, Quận 2, TP.HCM',
                'date_of_birth': date(1992, 5, 15),
                'gender': 'F',
                'bio': 'Huấn luyện viên chuyên về Yoga và Thiền',
                'certifications': 'Chứng chỉ Yoga 200h\nChứng chỉ Thiền định',
                'specialties': 'Yoga, Thiền, Thở',
                'hire_date': date(2023, 3, 1),
                'weekday_hourly_rate': 350000,
                'sunday_hourly_rate': 525000,
                'active': True
            },
            {
                'full_name': 'Lê Văn C',
                'phone': '0987654323',
                'address': '789 Đường DEF, Quận 3, TP.HCM',
                'date_of_birth': date(1988, 8, 20),
                'gender': 'M',
                'bio': 'Huấn luyện viên chuyên về thể hình và dinh dưỡng',
                'certifications': 'Chứng chỉ PT Quốc tế\nChứng chỉ Dinh dưỡng thể thao',
                'specialties': 'Thể hình, Dinh dưỡng, Crossfit',
                'hire_date': date(2023, 6, 1),
                'weekday_hourly_rate': 400000,
                'sunday_hourly_rate': 600000,
                'active': True
            }
        ]

        for data in instructors_data:
            instructor = Instructor.objects.create(**data)
            self.stdout.write(
                self.style.SUCCESS(f'Đã tạo huấn luyện viên: {instructor.full_name}')
            ) 