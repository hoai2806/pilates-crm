from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from django.template.response import TemplateResponse
from django.utils import timezone
import csv
import datetime
from .models import Payment, Expense

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'get_package_info', 'get_amount_display', 'get_discount_display', 'payment_date', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'payment_date', 'class_type')
    search_fields = ('invoice_number', 'customer__name', 'notes')
    date_hierarchy = 'payment_date'
    autocomplete_fields = ['customer', 'class_type']
    readonly_fields = ['invoice_number']
    actions = ['export_as_csv', 'mark_as_completed']
    change_list_template = 'admin/payments/payment/change_list.html'
    
    fieldsets = (
        ('Thông tin khách hàng', {
            'fields': ('invoice_number', 'customer')
        }),
        ('Thông tin gói dịch vụ', {
            'fields': ('class_type', 'amount')
        }),
        ('Thông tin khuyến mãi', {
            'fields': ('discount_type', 'discount_value')
        }),
        ('Thông tin thanh toán', {
            'fields': ('payment_date', 'payment_method', 'status', 'notes', 'payment_proof')
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('revenue-report/', self.admin_site.admin_view(self.revenue_report_view), name='revenue_report'),
            path('api/chart-data/', self.admin_site.admin_view(self.chart_data_view), name='payment_chart_data'),
        ]
        return custom_urls + urls
    
    def revenue_report_view(self, request):
        # Lấy dữ liệu báo cáo doanh thu
        today = timezone.now().date()
        
        # Thời gian báo cáo
        report_period = request.GET.get('period', 'month')
        if report_period == 'year':
            start_date = today.replace(month=1, day=1)
        elif report_period == 'quarter':
            current_month = today.month
            current_quarter = (current_month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start_date = today.replace(month=start_month, day=1)
        else:  # month
            start_date = today.replace(day=1)
        
        # Lấy tổng doanh thu trong khoảng thời gian
        completed_payments = Payment.objects.filter(
            status='completed',
            payment_date__gte=start_date,
            payment_date__lte=today
        )
        
        total_revenue = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
        payment_count = completed_payments.count()
        
        # Thống kê theo phương thức thanh toán
        payment_method_stats = completed_payments.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')
        
        # Thống kê theo loại lớp học
        class_type_stats = completed_payments.values('class_type__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')
        
        # Doanh thu theo ngày trong tháng hiện tại
        if report_period == 'month':
            daily_revenue = completed_payments.annotate(
                day=TruncDay('payment_date')
            ).values('day').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('day')
        else:
            daily_revenue = None
        
        # Doanh thu theo tháng trong năm hiện tại
        monthly_revenue = None
        if report_period == 'year' or report_period == 'quarter':
            monthly_revenue = completed_payments.annotate(
                month=TruncMonth('payment_date')
            ).values('month').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('month')
            
        # Chi phí trong kỳ báo cáo
        total_expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Lợi nhuận = Doanh thu - Chi phí
        profit = total_revenue - total_expenses
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Báo cáo doanh thu',
            'opts': self.model._meta,
            'period': report_period,
            'start_date': start_date,
            'end_date': today,
            'total_revenue': total_revenue,
            'payment_count': payment_count,
            'payment_method_stats': payment_method_stats,
            'class_type_stats': class_type_stats,
            'daily_revenue': daily_revenue,
            'monthly_revenue': monthly_revenue,
            'total_expenses': total_expenses,
            'profit': profit,
            'payment_method_choices': Payment.PAYMENT_METHOD_CHOICES,
        }
        
        return TemplateResponse(request, 'admin/payments/payment/revenue_report.html', context)
    
    def chart_data_view(self, request):
        """API trả về dữ liệu biểu đồ doanh thu"""
        today = timezone.now().date()
        start_date = today.replace(day=1)  # Mặc định: đầu tháng hiện tại
        
        period = request.GET.get('period', 'month')
        if period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today
            date_trunc = TruncMonth('payment_date')
            date_format = '%b'  # Tên tháng viết tắt
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = today
            date_trunc = TruncDay('payment_date')
            date_format = '%d'  # Ngày trong tháng
        elif period == 'week':
            # 7 ngày gần nhất
            start_date = today - datetime.timedelta(days=6)
            end_date = today
            date_trunc = TruncDay('payment_date')
            date_format = '%d/%m'  # Ngày/tháng
        
        # Lấy dữ liệu doanh thu
        revenue_data = Payment.objects.filter(
            status='completed',
            payment_date__gte=start_date,
            payment_date__lte=end_date
        ).annotate(
            date=date_trunc
        ).values('date').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('date')
        
        # Định dạng dữ liệu cho biểu đồ
        labels = []
        amounts = []
        counts = []
        
        for entry in revenue_data:
            if period == 'year':
                # Định dạng ngày tháng cho biểu đồ theo năm (hiển thị tháng)
                labels.append(entry['date'].strftime(date_format))
            else:
                # Định dạng ngày tháng cho biểu đồ theo tháng hoặc tuần
                labels.append(entry['date'].strftime(date_format))
            
            amounts.append(float(entry['total']))
            counts.append(entry['count'])
        
        # Trả về dữ liệu JSON cho biểu đồ
        return JsonResponse({
            'labels': labels,
            'amounts': amounts,
            'counts': counts,
        })
    
    def get_package_info(self, obj):
        if obj.class_type:
            return f"{obj.class_type.name}"
        return "-"
    get_package_info.short_description = "Gói dịch vụ"
    
    def get_amount_display(self, obj):
        # Sử dụng hàm clean_currency để chuyển đổi giá trị
        try:
            amount = float(obj.amount) if obj.amount is not None else 0
            return format_html('<span style="color: #333;">{:,.0f} đ</span>', amount)
        except (ValueError, TypeError):
            # Nếu có lỗi chuyển đổi, trả về giá trị gốc
            return str(obj.amount)
    get_amount_display.short_description = "Tổng tiền"
    
    def get_discount_display(self, obj):
        if not obj.discount_value:
            return "-"
        
        try:
            discount_value = float(obj.discount_value) if obj.discount_value is not None else 0
            
            if obj.discount_type == 'percentage':
                return format_html('<span style="color: #e74c3c;">{:,.0f}%</span>', discount_value)
            else:
                return format_html('<span style="color: #e74c3c;">{:,.0f} đ</span>', discount_value)
        except (ValueError, TypeError):
            # Nếu có lỗi chuyển đổi, trả về giá trị gốc
            return str(obj.discount_value)
    get_discount_display.short_description = "Giảm giá"
    
    def export_as_csv(self, request, queryset):
        """Xuất danh sách đơn hàng ra file CSV"""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=payments-{timezone.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)
        
        # Viết header
        writer.writerow([
            'Số hóa đơn', 'Khách hàng', 'Gói dịch vụ', 'Tổng tiền', 
            'Loại KM', 'Giảm giá', 'Thanh toán', 
            'Ngày thanh toán', 'Phương thức', 'Trạng thái', 'Ghi chú'
        ])
        
        # Viết dữ liệu
        for obj in queryset:
            package_info = f"{obj.class_type.name}" if obj.class_type else "-"
            discount_type_display = dict(Payment.DISCOUNT_TYPE_CHOICES).get(obj.discount_type, '')
            
            writer.writerow([
                obj.invoice_number or '',
                obj.customer.full_name,
                package_info,
                obj.amount,
                discount_type_display,
                obj.discount_value,
                obj.amount - obj.discount_value if obj.discount_type == 'amount' else obj.amount * (1 - obj.discount_value / 100) if obj.discount_type == 'percentage' else obj.amount,
                obj.payment_date.strftime('%d/%m/%Y'),
                dict(Payment.PAYMENT_METHOD_CHOICES).get(obj.payment_method, ''),
                dict(Payment.STATUS_CHOICES).get(obj.status, ''),
                obj.notes or ''
            ])
            
        return response
    export_as_csv.short_description = "Xuất danh sách đã chọn ra CSV"
    
    def mark_as_completed(self, request, queryset):
        """Đánh dấu các đơn hàng đã hoàn thành"""
        queryset.update(status='completed')
        self.message_user(request, f"Đã đánh dấu {queryset.count()} đơn hàng là hoàn thành")
    mark_as_completed.short_description = "Đánh dấu đã hoàn thành"
    
    def save_model(self, request, obj, form, change):
        # Tính toán số tiền cuối cùng dựa trên discount_type và discount_value
        if obj.discount_type and obj.discount_value:
            if obj.discount_type == 'percentage':
                # Giảm theo % 
                obj.amount = obj.amount * (1 - (obj.discount_value / 100))
            elif obj.discount_type == 'amount':
                # Giảm theo số tiền cụ thể
                obj.amount = max(0, obj.amount - obj.discount_value)
        
        # Lưu obj
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('css/custom_admin.css',),
        }
        js = ('js/price_format.js', 'js/payment_form.js')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'expense_date', 'description', 'paid_by')
    list_filter = ('category', 'expense_date')
    search_fields = ('description', 'paid_by')
    date_hierarchy = 'expense_date'
    
    fieldsets = (
        (None, {
            'fields': ('category', 'amount', 'expense_date', 'paid_by', 'description')
        }),
    )
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    get_category_display.short_description = "Loại chi phí"
