from django.db import models

# Create your models here.

class Branch(models.Model):
    # Thông tin cơ bản
    name = models.CharField(max_length=100, verbose_name="Tên chi nhánh")
    address = models.TextField(verbose_name="Địa chỉ")
    phone_number = models.CharField(max_length=20, verbose_name="Số điện thoại")
    google_map_url = models.URLField(verbose_name="Địa chỉ Google Map", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='branches/', blank=True, null=True, verbose_name="Hình ảnh")
    active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    
    # Tiện ích - Chung
    has_elevator = models.BooleanField(default=False, verbose_name="Thang máy")
    has_wifi = models.BooleanField(default=False, verbose_name="Wifi")
    has_lockers = models.BooleanField(default=False, verbose_name="Tủ khóa")
    has_shower = models.BooleanField(default=False, verbose_name="Phòng tắm")
    
    # Tiện ích - Bãi đỗ xe và Di chuyển
    has_parking = models.BooleanField(default=False, verbose_name="Bãi đỗ xe")
    has_bike_racks = models.BooleanField(default=False, verbose_name="Giá để xe đạp")
    has_accessible_parking = models.BooleanField(default=False, verbose_name="Bãi đỗ xe cho người khuyết tật")
    
    # Tiện ích - Khác
    has_towel_service = models.BooleanField(default=False, verbose_name="Dịch vụ khăn tắm")
    has_food_drink = models.BooleanField(default=False, verbose_name="Đồ ăn/thức uống")
    has_gender_neutral_restroom = models.BooleanField(default=False, verbose_name="Nhà vệ sinh không phân biệt giới tính")
    has_childcare = models.BooleanField(default=False, verbose_name="Dịch vụ trông trẻ")
    
    class Meta:
        verbose_name = "Chi nhánh"
        verbose_name_plural = "Chi nhánh"
        ordering = ['name']
    
    def __str__(self):
        return self.name
