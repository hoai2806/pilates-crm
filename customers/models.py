from django.db import models

# Create your models here.

class HealthDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('image', 'Hình ảnh'),
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('other', 'Khác')
    ]
    
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='health_documents')
    file = models.FileField(upload_to='health_documents/', verbose_name="Tài liệu sức khỏe")
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES, verbose_name="Loại tài liệu")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả tình trạng")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")
    
    # Thêm liên kết với thanh toán
    related_payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='health_documents',
                                     verbose_name="Thanh toán liên quan")
    
    # Thêm liên kết với điểm danh
    related_attendance = models.ForeignKey('classes.Attendance', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='health_documents',
                                        verbose_name="Buổi tập liên quan")
    
    class Meta:
        verbose_name = "Tài liệu sức khỏe"
        verbose_name_plural = "Tài liệu sức khỏe"
    
    def __str__(self):
        return f"Tài liệu sức khỏe của {self.customer.full_name}"

class CustomerActivity(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='activities', verbose_name="Khách hàng")
    content = models.TextField(verbose_name="Nội dung liên hệ")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian liên hệ")
    
    class Meta:
        verbose_name = "Hoạt động khách hàng"
        verbose_name_plural = "Hoạt động khách hàng"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Hoạt động của {self.customer.full_name} lúc {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

class Appointment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='appointments', verbose_name="Khách hàng")
    instructors = models.ManyToManyField('instructors.Instructor', related_name='appointments', verbose_name="Huấn luyện viên")
    appointment_date = models.DateTimeField(verbose_name="Ngày giờ hẹn")
    content = models.TextField(blank=True, null=True, verbose_name="Nội dung cuộc hẹn")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Cuộc hẹn"
        verbose_name_plural = "Cuộc hẹn"
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"Cuộc hẹn của {self.customer.full_name} lúc {self.appointment_date.strftime('%d/%m/%Y %H:%M')}"

class Customer(models.Model):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    )
    
    STATUS_CHOICES = (
        ('contact', 'Liên hệ'),
        ('trial', 'Tập thử'),
        ('purchased', 'Mua gói'),
        ('repurchased', 'Tái mua'),
        ('no_trial', 'Không đến tập thử'),
        ('no_purchase', 'Không mua'),
        ('no_repurchase', 'Không tái mua'),
    )
    
    SOURCE_CHOICES = (
        ('referral', 'Giới thiệu'),
        ('fanpage', 'Fanpage'),
        ('google_map', 'Google map'),
        ('direct', 'Trực tiếp'),
        ('social_media', 'Social media'),
        ('other', 'Kênh khác'),
    )
    
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Giới tính")
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Liên hệ khẩn cấp")
    health_issues = models.TextField(blank=True, null=True, verbose_name="Vấn đề sức khỏe")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    profile_image = models.ImageField(upload_to='customers/', blank=True, null=True, verbose_name="Ảnh đại diện")
    registration_date = models.DateField(auto_now_add=True, verbose_name="Ngày đăng ký")
    active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    
    # Thêm trường mới
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name="Bố/mẹ")
    parent_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Họ và tên bố/mẹ (nếu có)")
    parent_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại bố/mẹ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='contact', verbose_name="Trạng thái khách hàng")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct', verbose_name="Nguồn khách hàng")
    
    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name

class CustomerPackage(models.Model):
    STATUS_CHOICES = (
        ('active', 'Đang sử dụng'),
        ('pending', 'Chờ kích hoạt'),
        ('expired', 'Hết hạn'),
        ('used_up', 'Đã dùng hết buổi'),
        ('cancelled', 'Đã hủy'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='packages', verbose_name="Khách hàng")
    payment = models.OneToOneField('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_package', verbose_name="Đơn hàng")
    class_type = models.ForeignKey('classes.ClassType', on_delete=models.CASCADE, verbose_name="Loại lớp")
    total_sessions = models.PositiveIntegerField(verbose_name="Tổng số buổi")
    remaining_sessions = models.PositiveIntegerField(verbose_name="Số buổi còn lại")
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(blank=True, null=True, verbose_name="Ngày kết thúc")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Trạng thái")
    purchase_date = models.DateField(auto_now_add=True, verbose_name="Ngày mua")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    
    class Meta:
        verbose_name = "Gói tập"
        verbose_name_plural = "Gói tập"
        ordering = ['-purchase_date', 'status']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.class_type.name} ({self.remaining_sessions}/{self.total_sessions} buổi)"
    
    def use_session(self):
        """Sử dụng một buổi tập từ gói"""
        if self.remaining_sessions > 0 and self.status == 'active':
            self.remaining_sessions -= 1
            if self.remaining_sessions == 0:
                self.status = 'used_up'
            self.save()
            return True
        return False
