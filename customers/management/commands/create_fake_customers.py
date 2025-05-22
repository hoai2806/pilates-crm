from django.core.management.base import BaseCommand
from customers.models import Customer
from django.utils import timezone
import random
from datetime import timedelta
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Tạo dữ liệu khách hàng ảo'

    def handle(self, *args, **options):
        # Các mẫu dữ liệu
        ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Phan', 'Huỳnh']
        ten_dem_nam = ['Văn', 'Hữu', 'Đức', 'Công', 'Quốc', 'Minh', 'Hoàng', 'Anh']
        ten_dem_nu = ['Thị', 'Hồng', 'Ngọc', 'Bích', 'Thanh', 'Thu', 'Thùy', 'Kim']
        ten_nam = ['Nam', 'Hùng', 'Dũng', 'Quân', 'Tuấn', 'Hiếu', 'Đạt', 'Tùng', 'Quang', 'Trung']
        ten_nu = ['Hương', 'Lan', 'Linh', 'Thảo', 'Hà', 'Trang', 'Chi', 'Mai', 'Phương', 'Anh']
        
        dia_chi = [
            'Quận Hoàn Kiếm, Hà Nội',
            'Quận Ba Đình, Hà Nội',
            'Quận Cầu Giấy, Hà Nội',
            'Quận Đống Đa, Hà Nội',
            'Quận Hai Bà Trưng, Hà Nội',
            'Quận Hoàng Mai, Hà Nội',
            'Quận Long Biên, Hà Nội',
            'Quận Tây Hồ, Hà Nội',
            'Quận Thanh Xuân, Hà Nội',
            'Quận Hà Đông, Hà Nội'
        ]
        
        van_de_suc_khoe = [
            'Bàn chân bẹt', 
            'Vẹo cột sống', 
            'Trật khớp vai', 
            'Đau thắt lưng', 
            'Đau đầu gối', 
            'Gai cột sống', 
            'Viêm khớp cổ',
            'Không có vấn đề',
            'Hạn chế vận động',
            'Đau mắt cá chân'
        ]
        
        statuses = ['contact', 'trial', 'purchased', 'repurchased', 'no_trial', 'no_purchase', 'no_repurchase']
        sources = ['referral', 'fanpage', 'google_map', 'direct', 'social_media', 'other']
        
        now = timezone.now()
        
        # Tạo 10 khách hàng ảo
        customers_created = 0
        for i in range(10):
            # Random giới tính
            gender = random.choice(['M', 'F'])
            
            # Tạo họ tên theo giới tính
            if gender == 'M':
                full_name = f"{random.choice(ho)} {random.choice(ten_dem_nam)} {random.choice(ten_nam)}"
            else:
                full_name = f"{random.choice(ho)} {random.choice(ten_dem_nu)} {random.choice(ten_nu)}"
            
            # Random số điện thoại
            phone = f"09{random.randint(10000000, 99999999)}"
            
            # Random ngày sinh (18-65 tuổi)
            years_ago = random.randint(18, 65)
            days_variation = random.randint(-200, 200)
            date_of_birth = timezone.now().date() - timedelta(days=years_ago*365 + days_variation)
            
            # Random ngày đăng ký (1-180 ngày trước)
            registration_days_ago = random.randint(1, 180)
            registration_date = now.date() - timedelta(days=registration_days_ago)
            
            # Tạo dữ liệu khách hàng
            customer = Customer(
                full_name=full_name,
                phone=phone,
                date_of_birth=date_of_birth,
                gender=gender,
                address=random.choice(dia_chi),
                health_issues=random.choice(van_de_suc_khoe),
                notes=f"Khách hàng ảo #{i+1} tạo tự động",
                registration_date=registration_date,
                status=random.choice(statuses),
                source=random.choice(sources),
                active=random.choice([True, True, True, False])  # 75% khả năng là đang hoạt động
            )
            
            # Thêm thông tin phụ huynh cho 50% khách hàng
            if random.random() < 0.5:
                customer.parent_name = f"{random.choice(ho)} {random.choice(ten_dem_nam if random.random() < 0.7 else ten_dem_nu)} {random.choice(ten_nam if random.random() < 0.7 else ten_nu)}"
                customer.parent_phone = f"09{random.randint(10000000, 99999999)}"
            
            # Lưu khách hàng
            customer.save()
            customers_created += 1
            self.stdout.write(f"Đã tạo khách hàng: {customer.full_name}")
        
        self.stdout.write(self.style.SUCCESS(f'Đã tạo thành công {customers_created} khách hàng ảo')) 