from django.db import models
from django.utils import timezone
from customers.models import Customer
from classes.models import ClassType, ClassTypePrice
from instructors.models import Instructor
from branches.models import Branch

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tiền mặt'),
        ('bank_transfer', 'Chuyển khoản'),
        ('card', 'Thẻ'),
        ('other', 'Khác'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Đã hoàn thành'),
        ('pending', 'Chờ xử lý'),
        ('cancelled', 'Đã hủy'),
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('none', 'Không áp dụng'),
        ('percentage', 'Giảm theo %'),
        ('amount', 'Giảm theo số tiền'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('full', 'Thanh toán toàn bộ'),
        ('partial', 'Thanh toán một phần'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    class_type = models.ForeignKey(ClassType, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    # Thêm các trường mới
    invoice_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='none')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    
    # Thêm các trường liên quan đến thanh toán một phần
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='full')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0, 
                                     help_text="Số tiền đã thanh toán (chỉ áp dụng cho thanh toán một phần)")
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0,
                                          help_text="Số tiền còn lại cần thanh toán")
    remaining_payment_due_date = models.DateField(null=True, blank=True,
                                               help_text="Ngày đến hạn thanh toán số tiền còn lại")
    
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name='sold_payments', verbose_name='Người bán hàng (HLV)')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name='Chi nhánh')
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.amount} VNĐ - {self.payment_date}"
    
    @property
    def final_amount(self):
        """Tính toán số tiền sau khi áp dụng giảm giá"""
        if self.discount_type == 'percentage' and self.discount_value:
            return float(self.amount) * (1 - float(self.discount_value) / 100)
        elif self.discount_type == 'amount' and self.discount_value:
            return max(0, float(self.amount) - float(self.discount_value))
        return float(self.amount)
    
    def save(self, *args, **kwargs):
        # Tạo số hóa đơn tự động khi không có
        if not self.invoice_number:
            today = timezone.now()
            prefix = f"INV-{today.strftime('%Y%m%d')}-"
            last_invoice = Payment.objects.filter(
                invoice_number__startswith=prefix
            ).order_by('-invoice_number').first()
            
            if last_invoice:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                new_num = last_num + 1
                self.invoice_number = f"{prefix}{new_num:03d}"
            else:
                self.invoice_number = f"{prefix}001"
        
        # Tính giá trị sau khi giảm giá
        final_amount = self.final_amount
        
        # Cập nhật các giá trị liên quan đến thanh toán một phần
        if self.payment_type == 'partial':
            if self.paid_amount <= 0:
                self.paid_amount = final_amount * 0.5  # Mặc định trả 50% số tiền
            self.remaining_amount = final_amount - float(self.paid_amount)
            
            # Nếu chưa có ngày hạn thanh toán, thiết lập mặc định là 30 ngày sau
            if not self.remaining_payment_due_date:
                self.remaining_payment_due_date = timezone.now().date() + timezone.timedelta(days=30)
        else:
            # Thanh toán toàn bộ
            self.paid_amount = final_amount
            self.remaining_amount = 0
            self.remaining_payment_due_date = None
                
        super().save(*args, **kwargs)

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Tiền thuê'),
        ('salary', 'Lương nhân viên'),
        ('utility', 'Tiện ích'),
        ('maintenance', 'Bảo trì'),
        ('inventory', 'Nhập kho'),
        ('marketing', 'Marketing'),
        ('other', 'Khác'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(blank=True, null=True)
    expense_date = models.DateField(default=timezone.now)
    paid_by = models.CharField(max_length=100, default='Admin')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-expense_date']
        verbose_name = "Chi phí"
        verbose_name_plural = "Chi phí"
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} VNĐ - {self.expense_date}"
