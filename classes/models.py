from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from instructors.models import Instructor
from customers.models import Customer, CustomerPackage
from branches.models import Branch

class ClassType(models.Model):
    CLASS_CATEGORY_CHOICES = (
        ('fixed', 'Lớp cố định'),
        ('registration', 'Lớp đăng ký'),
        ('trial', 'Lớp tập thử'),
    )
    
    name = models.CharField(max_length=100, verbose_name="Tên loại lớp")
    description = models.TextField(verbose_name="Mô tả", blank=True, null=True)
    branches = models.ManyToManyField(Branch, related_name="class_types", verbose_name="Chi nhánh áp dụng")
    duration = models.PositiveIntegerField(verbose_name="Thời lượng (phút)")
    max_capacity = models.PositiveIntegerField(verbose_name="Sức chứa tối đa")
    difficulty_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Mức độ khó (1-5)"
    )
    class_category = models.CharField(
        max_length=20, 
        choices=CLASS_CATEGORY_CHOICES, 
        default='registration', 
        verbose_name="Loại lớp"
    )
    
    class Meta:
        verbose_name = "Loại lớp học"
        verbose_name_plural = "Loại lớp học"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ClassTypePrice(models.Model):
    CLASS_FORMAT_CHOICES = (
        ('PT', 'PT 1:1'),
        ('GROUP_2', 'Nhóm 1:2'),
        ('GROUP_3', 'Nhóm 1:3'),
        ('GROUP_6', 'Nhóm 1:6'),
    )
    
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, related_name="prices", verbose_name="Loại lớp")
    class_format = models.CharField(max_length=20, choices=CLASS_FORMAT_CHOICES, verbose_name="Hình thức lớp")
    time_slot = models.CharField(
        max_length=20,
        choices=[
            ('ALL', 'Tất cả khung giờ'),
            ('MORNING_LOW', 'Thấp điểm sáng'),
            ('MORNING_MID', 'Trung điểm sáng'),
            ('MORNING_PEAK', 'Cao điểm sáng'),
            ('AFTERNOON_LOW', 'Thấp điểm chiều'),
            ('AFTERNOON_MID', 'Trung điểm chiều'),
            ('AFTERNOON_PEAK', 'Cao điểm chiều'),
        ],
        default='ALL',
        verbose_name='Khung giờ',
    )
    number_of_sessions = models.PositiveIntegerField(verbose_name="Số buổi")
    unit_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Đơn giá")
    order = models.PositiveIntegerField(default=0)
    
    @property
    def total_price(self):
        return self.number_of_sessions * self.unit_price
    
    class Meta:
        verbose_name = "Bảng giá lớp học"
        verbose_name_plural = "Bảng giá lớp học"
        ordering = ['order', 'class_format', 'number_of_sessions']
        unique_together = ['class_type', 'class_format', 'time_slot', 'number_of_sessions']
    
    def __str__(self):
        return f"{self.get_class_format_display()} - {self.number_of_sessions} buổi"

class ClassSchedule(models.Model):
    DAY_CHOICES = (
        (0, 'Thứ 2'),
        (1, 'Thứ 3'),
        (2, 'Thứ 4'),
        (3, 'Thứ 5'),
        (4, 'Thứ 6'),
        (5, 'Thứ 7'),
        (6, 'Chủ nhật'),
    )
    
    STATUS_CHOICES = (
        ('scheduled', 'Đã lên lịch'),
        ('ongoing', 'Đang diễn ra'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, verbose_name="Loại lớp")
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, verbose_name="Huấn luyện viên")
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="Ngày trong tuần")
    start_time = models.TimeField(verbose_name="Giờ bắt đầu")
    end_time = models.TimeField(verbose_name="Giờ kết thúc")
    active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    room = models.CharField(max_length=50, verbose_name="Phòng")
    
    # Thông tin ngày cụ thể (nếu là buổi học riêng lẻ, không phải lịch lặp lại)
    specific_date = models.DateField(blank=True, null=True, verbose_name="Ngày cụ thể")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Trạng thái", 
                             help_text="Chỉ áp dụng cho buổi học cụ thể")
    actual_start_time = models.TimeField(blank=True, null=True, verbose_name="Thời gian bắt đầu thực tế")
    actual_end_time = models.TimeField(blank=True, null=True, verbose_name="Thời gian kết thúc thực tế")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    
    # Thêm các trường cho repeater
    is_recurring = models.BooleanField(default=False, verbose_name="Lặp lại hàng tuần")
    recurring_days = models.JSONField(blank=True, null=True, verbose_name="Các ngày lặp lại", 
                                    help_text="Danh sách các ngày trong tuần lặp lại (0: Thứ 2, 1: Thứ 3, ...)")
    start_date = models.DateField(blank=True, null=True, verbose_name="Ngày bắt đầu")
    end_date = models.DateField(blank=True, null=True, verbose_name="Ngày kết thúc", 
                               help_text="Để trống nếu lặp lại vô hạn")
    
    # Nếu buổi học được tạo từ lịch lặp lại, lưu thông tin lịch gốc
    parent_schedule = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, 
                                       related_name='child_schedules', verbose_name="Lịch học gốc")
    
    class Meta:
        verbose_name = "Lịch học"
        verbose_name_plural = "Lịch học"
        ordering = ['specific_date', 'day_of_week', 'start_time']
    
    def __str__(self):
        if self.specific_date:
            return f"{self.class_type.name} - {self.specific_date.strftime('%d/%m/%Y')} {self.start_time.strftime('%H:%M')}"
        return f"{self.class_type.name} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}"
        
    def clean(self):
        super().clean()
        # Chỉ kiểm tra cho các buổi học cụ thể (không phải template lịch lặp lại)
        if self.specific_date and self.start_time and self.end_time and self.instructor:
            # Kiểm tra nếu end_time trước start_time
            if self.end_time <= self.start_time:
                raise ValidationError({'end_time': "Giờ kết thúc phải sau giờ bắt đầu."})

            # Tìm các lịch học khác của cùng giáo viên vào cùng ngày cụ thể
            conflicting_schedules = ClassSchedule.objects.filter(
                instructor=self.instructor,
                specific_date=self.specific_date,
                # Loại trừ chính nó nếu đang cập nhật
            ).exclude(pk=self.pk if self.pk else None)

            for schedule in conflicting_schedules:
                # Kiểm tra chồng chéo thời gian
                # (NewStart < ExistingEnd) AND (NewEnd > ExistingStart)
                if self.start_time < schedule.end_time and self.end_time > schedule.start_time:
                    raise ValidationError(
                        f"Giáo viên {self.instructor} đã có lịch dạy từ {schedule.start_time.strftime('%H:%M')} đến {schedule.end_time.strftime('%H:%M')} "
                        f"vào ngày {self.specific_date.strftime('%d/%m/%Y')}. Vui lòng chọn thời gian khác."
                    )
        
        # Kiểm tra cho lịch lặp lại (recurring schedule)
        if self.is_recurring and self.start_date and self.recurring_days:
            if self.end_date and self.end_date < self.start_date:
                raise ValidationError({'end_date': "Ngày kết thúc lặp lại phải sau hoặc bằng ngày bắt đầu."})
            if self.end_time <= self.start_time:
                raise ValidationError({'end_time': "Giờ kết thúc phải sau giờ bắt đầu cho lịch lặp lại."})
            
            # (Tùy chọn nâng cao) Bạn có thể thêm logic kiểm tra trùng lặp cho các template lịch lặp lại ở đây.
            # Ví dụ: không cho phép tạo 2 lịch lặp lại của cùng giáo viên vào cùng thứ và giờ.
            # Tuy nhiên, logic này phức tạp hơn vì phải so sánh day_of_week/recurring_days và start_time/end_time.
            # Hiện tại, chỉ tập trung vào các buổi học cụ thể (specific_date).

    def save(self, *args, **kwargs):
        # Đảm bảo các lớp fixed được đặt là lặp lại
        if hasattr(self, 'class_type') and self.class_type and self.class_type.class_category == 'fixed':
            self.is_recurring = True
            
        super().save(*args, **kwargs)
        
        # Nếu là lịch lặp lại và có ngày bắt đầu, tạo các buổi học tương ứng
        if not self.specific_date and self.is_recurring and self.start_date:
            self.generate_class_sessions()
    
    def generate_class_sessions(self):
        """Tạo các buổi học dựa trên lịch lặp lại"""
        from datetime import datetime, timedelta
        import pytz
        
        # Xóa các buổi học tương lai đã được tạo trước đó mà chưa thay đổi trạng thái
        future_date = datetime.now().date()
        ClassSchedule.objects.filter(
            parent_schedule=self, 
            specific_date__gte=future_date,
            status='scheduled'
        ).delete()
        
        # Tạo danh sách các ngày lặp lại
        recurring_days = self.recurring_days or [self.day_of_week]
        
        # Tính ngày bắt đầu
        current_date = max(self.start_date, datetime.now().date())
        
        # Tính ngày kết thúc (mặc định tạo trước 3 tháng nếu không có ngày kết thúc)
        end_date = self.end_date or (current_date + timedelta(days=90))
        
        # Tạo các buổi học
        while current_date <= end_date:
            weekday = current_date.weekday()
            
            # Nếu ngày hiện tại là một trong các ngày lặp lại
            if weekday in recurring_days:
                # Tạo buổi học mới
                ClassSchedule.objects.create(
                    parent_schedule=self,
                    class_type=self.class_type,
                    instructor=self.instructor,
                    day_of_week=weekday,
                    start_time=self.start_time,
                    end_time=self.end_time,
                    specific_date=current_date,
                    status='scheduled',
                    room=self.room,
                    active=self.active,
                    is_recurring=False  # Buổi học cụ thể không lặp lại
                )
            
            current_date += timedelta(days=1)
    
    @property
    def is_session(self):
        """Kiểm tra xem đây có phải là một buổi học cụ thể hay không"""
        return self.specific_date is not None
    
    @property 
    def calendar_color(self):
        """Trả về màu hiển thị trên lịch dựa trên loại lớp"""
        if hasattr(self, 'class_type') and self.class_type:
            if self.class_type.class_category == 'fixed':
                return '#4CAF50'  # Xanh lá cho lớp cố định
            elif self.class_type.class_category == 'registration':
                return '#2196F3'  # Xanh dương cho lớp đăng ký
            elif self.class_type.class_category == 'trial':
                return '#FFC107'  # Vàng cho lớp thử
        return '#9E9E9E'  # Màu mặc định

class Attendance(models.Model):
    class_session = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, verbose_name="Buổi học")
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, verbose_name="Khách hàng")
    attended = models.BooleanField(default=False, verbose_name="Đã tham dự")
    time_in = models.TimeField(blank=True, null=True, verbose_name="Giờ vào")
    time_out = models.TimeField(blank=True, null=True, verbose_name="Giờ ra")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    customer_package = models.ForeignKey("customers.CustomerPackage", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Gói tập sử dụng")
    is_session_deducted = models.BooleanField(default=False, verbose_name="Đã trừ buổi tập")
    
    class Meta:
        verbose_name = "Điểm danh"
        verbose_name_plural = "Điểm danh"
        unique_together = ['class_session', 'customer']
    
    def __str__(self):
        return f"{self.customer} - {self.class_session}"
    
    def save(self, *args, **kwargs):
        # Nếu đã điểm danh nhưng chưa trừ buổi
        is_new = self.pk is None
        was_attended = False if is_new else Attendance.objects.get(pk=self.pk).attended
        
        # Nếu mới được điểm danh và chưa trừ buổi tập
        if self.attended and not self.is_session_deducted and (is_new or not was_attended):
            # Tìm gói tập của khách hàng phù hợp với loại lớp của buổi học
            packages = CustomerPackage.objects.filter(
                customer=self.customer,
                class_type=self.class_session.class_type,
                status='active',
                remaining_sessions__gt=0
            ).order_by('end_date')  # Ưu tiên gói sắp hết hạn trước
            
            # Nếu tìm thấy gói tập phù hợp, trừ một buổi
            if packages.exists():
                package = packages.first()
                if package.use_session():
                    self.customer_package = package
                    self.is_session_deducted = True
        
        super().save(*args, **kwargs)

# booking_deadline_days = models.PositiveIntegerField(default=1, verbose_name="Hạn chót đặt lịch (ngày)")

# ct = ClassType.objects.get(id=20)  # Bàn chân bẹt - Nhóm 1:6 - X-Pilates

# @receiver(post_save, sender=ClassTypePrice)
