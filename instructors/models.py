from django.db import models

# Create your models here.

class Instructor(models.Model):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    )
    
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Giới tính")
    bio = models.TextField(blank=True, null=True, verbose_name="Tiểu sử")
    certifications = models.TextField(blank=True, null=True, verbose_name="Chứng chỉ")
    specialties = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chuyên môn")
    profile_image = models.ImageField(upload_to='instructors/', blank=True, null=True, verbose_name="Ảnh đại diện")
    hire_date = models.DateField(verbose_name="Ngày thuê")
    weekday_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Mức lương theo giờ (Thứ 2-7)", blank=True, null=True)
    sunday_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Mức lương theo giờ (Chủ nhật)", blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name="Đang làm việc")
    
    class Meta:
        verbose_name = "Huấn luyện viên"
        verbose_name_plural = "Huấn luyện viên"
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
