from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.paginator import Paginator
import json # Import json để truyền an toàn vào template

# Import các model
from customers.models import Customer, CustomerPackage
from payments.models import Payment, Expense
from classes.models import ClassSchedule, Attendance
from instructors.models import Instructor
from .forms import CustomerForm # Thêm import CustomerForm

def index(request):
    # Dữ liệu thống kê tổng quan
    total_customers = Customer.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    total_orders = Payment.objects.filter(status='completed').count()
    total_visits = Attendance.objects.filter(attended=True).count()
    
    # Thống kê khách hàng mới trong 30 ngày qua
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    new_customers = Customer.objects.filter(registration_date__gte=thirty_days_ago).count()
    
    # Lấy 3 thanh toán gần nhất
    recent_payments = Payment.objects.filter(status='completed').select_related('customer')[:3]
    
    # Lấy 3 buổi học sắp tới
    upcoming_classes = ClassSchedule.objects.filter(
        specific_date__gte=timezone.now().date(),
        status='scheduled'
    ).select_related('class_type', 'instructor').order_by('specific_date', 'start_time')[:3]
    
    # Lấy 3 khách hàng mới đăng ký gần đây nhất
    new_registrations = Customer.objects.order_by('-registration_date')[:3]
    
    return render(request, 'reback/dashboard.html', {
        'title': 'Dashboard',
        # Dữ liệu thống kê
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_visits': total_visits,
        'new_customers': new_customers,
        
        # Dữ liệu chi tiết
        'recent_payments': recent_payments,
        'upcoming_classes': upcoming_classes,
        'new_registrations': new_registrations,
    })

def customers(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    customers_query = Customer.objects.all()
    date_filter_applied = False

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            customers_query = customers_query.filter(registration_date__gte=start_date)
            date_filter_applied = True
        except ValueError:
            start_date = None # Hoặc xử lý lỗi theo cách khác
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Để bao gồm cả ngày kết thúc, ta cần tìm các bản ghi nhỏ hơn hoặc bằng ngày đó
            customers_query = customers_query.filter(registration_date__lte=end_date)
            date_filter_applied = True
        except ValueError:
            end_date = None # Hoặc xử lý lỗi theo cách khác

    # Dữ liệu thống kê trạng thái khách hàng (cập nhật dựa trên customers_query)
    status_counts = customers_query.values('status').annotate(count=Count('id')).order_by('status')
    customer_status_data = {status_key: 0 for status_key, _ in Customer.STATUS_CHOICES}
    for item in status_counts:
        if item['status'] in customer_status_data:
            customer_status_data[item['status']] = item['count']
    
    # Dữ liệu cho biểu đồ (cập nhật dựa trên customer_status_data đã lọc)
    chart_labels_list = [label for _, label in Customer.STATUS_CHOICES]
    chart_data_list = [customer_status_data.get(key, 0) for key, _ in Customer.STATUS_CHOICES]

    # Lấy khách hàng cho bảng Kanban (cập nhật dựa trên customers_query)
    kanban_statuses = [
        'contact', 'trial', 'purchased', 'repurchased', 
        'no_trial', 'no_purchase', 'no_repurchase'
    ]
    customers_for_kanban = {}
    for status_key in kanban_statuses:
        # Lọc thêm theo status_key từ customers_query đã được lọc ngày (nếu có)
        customers_for_kanban[status_key] = customers_query.filter(status=status_key).order_by('-registration_date')[:5]

    context = {
        'title': 'Dashboard Khách hàng',
        'customer_status_data': customer_status_data,
        'chart_labels': json.dumps(chart_labels_list), 
        'chart_data': json.dumps(chart_data_list),
        'customer_status_choices': Customer.STATUS_CHOICES, 
        'customers_for_kanban': customers_for_kanban,
        'kanban_status_map': {key: display_name for key, display_name in Customer.STATUS_CHOICES if key in kanban_statuses},
        'start_date': start_date_str, # Truyền lại để hiển thị trên form
        'end_date': end_date_str      # Truyền lại để hiển thị trên form
    }
    return render(request, 'reback/customers.html', context)

def schedules(request):
    # Lấy lịch học
    schedules_list = ClassSchedule.objects.filter(
        specific_date__gte=timezone.now().date()
    ).select_related('class_type', 'instructor').order_by('specific_date', 'start_time')
    
    # Phân trang
    paginator = Paginator(schedules_list, 10)  # Hiển thị 10 lịch học mỗi trang
    page_number = request.GET.get('page', 1)
    schedules_page = paginator.get_page(page_number)
    
    # Thống kê cho dashboard lịch học
    total_schedules = ClassSchedule.objects.filter(specific_date__gte=timezone.now().date()).count()
    scheduled_classes = ClassSchedule.objects.filter(status='scheduled', specific_date__gte=timezone.now().date()).count()
    cancelled_classes = ClassSchedule.objects.filter(status='cancelled', specific_date__gte=timezone.now().date()).count()
    completed_classes = ClassSchedule.objects.filter(status='completed').count()
    
    # Lấy danh sách huấn luyện viên có lịch dạy trong tuần tới
    one_week_later = timezone.now().date() + timedelta(days=7)
    instructors_this_week = Instructor.objects.filter(
        classschedule__specific_date__gte=timezone.now().date(),
        classschedule__specific_date__lte=one_week_later
    ).distinct()
    
    return render(request, 'reback/schedules.html', {
        'title': 'Lịch học',
        'schedules': schedules_page,
        
        # Dữ liệu dashboard lịch học
        'total_schedules': total_schedules,
        'scheduled_classes': scheduled_classes,
        'cancelled_classes': cancelled_classes,
        'completed_classes': completed_classes,
        'instructors_this_week': instructors_this_week,
    })

def payments(request):
    # Lấy danh sách thanh toán
    payments_list = Payment.objects.all().select_related('customer').order_by('-payment_date')
    
    # Phân trang
    paginator = Paginator(payments_list, 10)  # Hiển thị 10 thanh toán mỗi trang
    page_number = request.GET.get('page', 1)
    payments_page = paginator.get_page(page_number)
    
    return render(request, 'reback/payments.html', {
        'title': 'Đơn hàng',
        'payments': payments_page,
    })

def instructors(request):
    # Lấy danh sách huấn luyện viên
    instructors_list = Instructor.objects.all()
    
    # Phân trang
    paginator = Paginator(instructors_list, 12)  # Hiển thị 12 huấn luyện viên mỗi trang
    page_number = request.GET.get('page', 1)
    instructors_page = paginator.get_page(page_number)
    
    return render(request, 'reback/instructors.html', {
        'title': 'Huấn luyện viên',
        'instructors': instructors_page,
    })

# --- Customer CRUD Views (Reback Theme) ---

def customer_add_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Thêm messages success ở đây nếu muốn
            return redirect('reback:customers')
    else:
        form = CustomerForm()
    return render(request, 'reback/customer_form.html', {
        'title': 'Thêm Khách Hàng Mới',
        'form': form,
        'form_title': 'Tạo hồ sơ khách hàng',
        'submit_button_text': 'Thêm Khách Hàng'
    })

def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    purchase_history = CustomerPackage.objects.filter(customer=customer).order_by('-purchase_date')
    attendance_history = Attendance.objects.filter(customer=customer).select_related('class_session', 'class_session__class_type', 'customer_package').order_by('-class_session__specific_date', '-class_session__start_time')
    activity_history = customer.activities.all().order_by('-timestamp') #Sử dụng related_name 'activities'

    return render(request, 'reback/customer_detail.html', {
        'title': f'Chi Tiết: {customer.full_name}',
        'customer': customer,
        'purchase_history': purchase_history,
        'attendance_history': attendance_history,
        'activity_history': activity_history,
    })

def customer_edit_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            # Thêm messages success ở đây nếu muốn
            return redirect('reback:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'reback/customer_form.html', {
        'title': f'Chỉnh Sửa: {customer.full_name}',
        'form': form,
        'customer': customer, # Để hiển thị thông tin thêm nếu cần
        'form_title': f'Cập nhật hồ sơ cho {customer.full_name}',
        'submit_button_text': 'Lưu Thay Đổi'
    })

def customer_delete_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        # Thêm messages success ở đây nếu muốn
        return redirect('reback:customers')
    return render(request, 'reback/customer_confirm_delete.html', {
        'title': f'Xác Nhận Xóa: {customer.full_name}',
        'customer': customer
    })

# --- End Customer CRUD Views ---
