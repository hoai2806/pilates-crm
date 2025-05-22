import json
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum, Case, When, BooleanField, IntegerField, Value
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ClassScheduleForm
from customers.models import Customer, CustomerPackage, HealthDocument
from classes.models import ClassType, ClassSchedule, Attendance
from instructors.models import Instructor
from branches.models import Branch
from payments.models import Payment
from django.contrib.auth.models import User
import calendar
from dateutil.relativedelta import relativedelta

# Create your views here.

@login_required
def customer_dashboard(request):
    # Lấy thời gian từ filter hoặc mặc định là tất cả
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Chuẩn bị bộ lọc
    filter_params = {}
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            filter_params['registration_date__range'] = [start_date, end_date]
        except ValueError:
            pass
    
    # Lấy tất cả khách hàng theo trạng thái thực
    contact_customers = list(Customer.objects.filter(status='contact', **filter_params).order_by('-registration_date')[:10])
    trial_customers = list(Customer.objects.filter(status='trial', **filter_params).order_by('-registration_date')[:10])
    purchased_customers = list(Customer.objects.filter(status='purchased', **filter_params).order_by('-registration_date')[:10])
    repurchased_customers = list(Customer.objects.filter(status='repurchased', **filter_params).order_by('-registration_date')[:10])
    no_trial_customers = list(Customer.objects.filter(status='no_trial', **filter_params).order_by('-registration_date')[:10])
    no_purchase_customers = list(Customer.objects.filter(status='no_purchase', **filter_params).order_by('-registration_date')[:10])
    no_repurchase_customers = list(Customer.objects.filter(status='no_repurchase', **filter_params).order_by('-registration_date')[:10])
    
    # Thống kê số lượng khách hàng theo trạng thái
    customer_stats = Customer.objects.filter(**filter_params).values('status').annotate(count=Count('id'))
    stats_dict = {item['status']: item['count'] for item in customer_stats}
    
    # Tạo các tùy chọn thời gian
    today = timezone.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    this_year_start = today.replace(month=1, day=1)
    
    # Tính toán các số liệu tổng hợp
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(active=True).count()
    purchased_count = Customer.objects.filter(status__in=['purchased', 'repurchased']).count()
    new_customers_this_month = Customer.objects.filter(registration_date__gte=this_month_start).count()
    
    context = {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'purchased_customers_count': purchased_count,
        'new_customers_this_month': new_customers_this_month,
        
        # Danh sách khách hàng theo trạng thái thực
        'contact_customers': contact_customers,           # Khách hàng liên hệ
        'trial_customers': trial_customers,               # Khách hàng tập thử
        'purchased_customers': purchased_customers,       # Khách hàng đã mua
        'repurchased_customers': repurchased_customers,   # Khách hàng tái mua
        'no_trial_customers': no_trial_customers,         # Khách hàng không đến tập thử
        'no_purchase_customers': no_purchase_customers,   # Khách hàng không mua hàng
        'no_repurchase_customers': no_repurchase_customers, # Khách hàng không tái mua
        
        'stats': stats_dict,
        'start_date': start_date,
        'end_date': end_date,
        'presets': {
            'today': today,
            'this_week': this_week_start,
            'this_month': this_month_start,
            'this_year': this_year_start,
        }
    }
    
    return render(request, 'dashboard/customer_dashboard.html', context)

@login_required
def main_dashboard_view(request):
    context = {
        'welcome_message': f"Chào mừng {request.user.username} đến với trang quản trị tùy chỉnh!",
        # Bạn có thể thêm các dữ liệu khác cho dashboard ở đây sau này
    }
    return render(request, 'dashboard/main_dashboard.html', context)

@login_required
def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    health_documents = HealthDocument.objects.filter(customer=customer)
    purchase_history = CustomerPackage.objects.filter(customer=customer).order_by('-purchase_date')
    attendance_history = Attendance.objects.filter(customer=customer).select_related('class_session', 'class_session__class_type', 'customer_package').order_by('-class_session__specific_date', '-class_session__start_time')
    activity_history = customer.activities.all().order_by('-timestamp') if hasattr(customer, 'activities') else []
    context = {
        'customer': customer,
        'health_documents': health_documents,
        'purchase_history': purchase_history,
        'attendance_history': attendance_history,
        'activity_history': activity_history,
    }
    return render(request, 'dashboard/customer_detail.html', context)

@login_required
def customer_edit_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        # Xử lý dữ liệu form
        customer.full_name = request.POST.get('full_name')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        if request.POST.get('date_of_birth'):
            customer.date_of_birth = request.POST.get('date_of_birth')
        customer.gender = request.POST.get('gender')
        customer.emergency_contact = request.POST.get('emergency_contact')
        customer.health_issues = request.POST.get('health_issues')
        customer.notes = request.POST.get('notes')
        customer.parent_id = request.POST.get('parent')
        customer.parent_name = request.POST.get('parent_name')
        customer.parent_phone = request.POST.get('parent_phone')
        customer.status = request.POST.get('status')
        customer.source = request.POST.get('source')
        customer.active = 'active' in request.POST
        
        # Xử lý hình ảnh
        if 'profile_image' in request.FILES:
            customer.profile_image = request.FILES['profile_image']
        
        customer.save()
        
        # Xử lý tài liệu sức khỏe mới
        if 'health_documents' in request.FILES:
            for file in request.FILES.getlist('health_documents'):
                # Xác định loại file
                file_name = file.name.lower()
                if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    doc_type = 'image'
                elif file_name.endswith('.pdf'):
                    doc_type = 'pdf'
                elif file_name.endswith(('.mp4', '.avi', '.mov', '.wmv')):
                    doc_type = 'video'
                else:
                    doc_type = 'other'
                
                # Lấy thông tin mô tả và các liên kết
                description = request.POST.get('health_documents_description', '')
                related_payment_id = request.POST.get('health_doc_payment')
                related_attendance_id = request.POST.get('health_doc_attendance')
                
                # Tạo document mới
                doc = HealthDocument(
                    customer=customer,
                    file=file,
                    document_type=doc_type,
                    description=description
                )
                
                # Thiết lập liên kết nếu có
                if related_payment_id:
                    try:
                        payment = Payment.objects.get(id=related_payment_id, customer=customer)
                        doc.related_payment = payment
                    except Payment.DoesNotExist:
                        pass
                
                if related_attendance_id:
                    try:
                        attendance = Attendance.objects.get(id=related_attendance_id, customer=customer)
                        doc.related_attendance = attendance
                    except Attendance.DoesNotExist:
                        pass
                
                doc.save()
        
        # Tạo activity sau khi cập nhật
        CustomerActivity.objects.create(
            customer=customer,
            content=f"Khách hàng được cập nhật thông tin bởi {request.user}"
        )
        
        messages.success(request, "Cập nhật khách hàng thành công!")
        return redirect('dashboard:customer_detail', pk=customer.pk)
    
    # Lấy danh sách thanh toán và điểm danh của khách hàng
    payments = Payment.objects.filter(customer=customer)
    attendances = Attendance.objects.filter(customer=customer)
    
    context = {
        'customer': customer,
        'payments': payments,
        'attendances': attendances,
    }
    return render(request, 'dashboard/customer_edit.html', context)

@login_required
def get_calendar_events(request):
    """API trả về events cho FullCalendar, bao gồm Lịch học và Cuộc hẹn"""
    print(f"--- NEW REQUEST get_calendar_events ---") # LOG START
    try:
        start_param = request.GET.get('start')
        end_param = request.GET.get('end')
        view_type = request.GET.get('view_type', 'timeGridWeek')
        print(f"Received params: start={start_param}, end={end_param}, view_type={view_type}") # LOG PARAMS

        try:
            start_date = datetime.fromisoformat(start_param.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_param.replace('Z', '+00:00'))
            print(f"Parsed dates: start_date={start_date}, end_date={end_date}") # LOG PARSED DATES
        except (ValueError, AttributeError, TypeError) as e_parse: # Added TypeError
            print(f"Error parsing date parameters: {e_parse}. Falling back to default.") # LOG PARSE ERROR
            now = datetime.now()
            start_date = now - timedelta(days=now.weekday())
            end_date = start_date + timedelta(days=7)
        
        cache_key = f'calendar_events:{start_date.date()}:{end_date.date()}:{view_type}'
        # cached_events = cache.get(cache_key) # Tạm thời tắt cache để debug
        # if cached_events:
        #     print("Returning cached events.")
        #     return JsonResponse(cached_events, safe=False)
            
        events = []
        
        if view_type == 'dayGridMonth':
            schedule_limit = 300  # Tăng giới hạn để hiển thị đầy đủ lịch học
            appointment_limit = 100 # Tăng giới hạn cuộc hẹn
            print(f"Month view: schedule_limit={schedule_limit}, appointment_limit={appointment_limit}")
        elif view_type == 'timeGridWeek':
            schedule_limit = 150 # Tăng giới hạn
            appointment_limit = 50
        else: 
            schedule_limit = 100
            appointment_limit = 50

        print("Querying ClassSchedules...")
        class_schedules = ClassSchedule.objects.filter(
            Q(specific_date__isnull=False, specific_date__gte=start_date.date(), specific_date__lte=end_date.date()) |
            Q(is_recurring=True, start_date__lte=end_date.date()) &
            (Q(end_date__isnull=True) | Q(end_date__gte=start_date.date()))
        ).select_related('class_type', 'instructor').order_by('specific_date', 'start_time')
        print(f"Found {class_schedules.count()} raw class_schedules before processing.")
        
        processed_schedule_ids = set()
        temp_schedule_events = []
        for schedule_idx, schedule in enumerate(class_schedules):
            print(f"Processing schedule ID {schedule.id} (type: {'specific' if schedule.specific_date else 'recurring'})")
            try:
                if schedule.specific_date:
                    if f'class_{schedule.id}' not in processed_schedule_ids:
                        if not schedule.start_time or not schedule.end_time: # Thêm kiểm tra
                            print(f"Skipping specific schedule ID {schedule.id} due to missing start/end time.")
                            continue
                        start_datetime = datetime.combine(schedule.specific_date, schedule.start_time)
                        end_datetime = datetime.combine(schedule.specific_date, schedule.end_time)
                        temp_schedule_events.append({
                            'id': f'event_class_{schedule.id}',
                            'title': f'{schedule.class_type.name if schedule.class_type else "N/A"} (Lớp)',
                            'start': start_datetime.isoformat(),
                            'end': end_datetime.isoformat(),
                            'color': schedule.calendar_color or '#3788d8',
                            'extendedProps': {
                                'type': 'class',
                                'schedule_id': schedule.id,
                                'class_name': schedule.class_type.name if schedule.class_type else 'N/A',
                                'instructor_name': schedule.instructor.full_name if schedule.instructor else 'N/A',
                                'room': schedule.room or 'N/A',
                                'status': schedule.status if schedule.status else 'N/A'
                            }
                        })
                        processed_schedule_ids.add(f'class_{schedule.id}')
                elif schedule.is_recurring: 
                    if not schedule.start_time or not schedule.end_time: # Thêm kiểm tra
                        print(f"Skipping recurring master schedule ID {schedule.id} due to missing start/end time on master.")
                        continue 
                    current_iter_date = max(schedule.start_date, start_date.date())
                    recurring_series_end_date = schedule.end_date if schedule.end_date else end_date.date()
                    iteration_limit_date = min(recurring_series_end_date, end_date.date())
                    while current_iter_date <= iteration_limit_date:
                        if current_iter_date.weekday() in (schedule.recurring_days or []):
                            event_id = f'event_recurring_{schedule.id}_{current_iter_date.isoformat()}'
                            if event_id not in processed_schedule_ids:
                                start_datetime = datetime.combine(current_iter_date, schedule.start_time)
                                end_datetime = datetime.combine(current_iter_date, schedule.end_time)
                                temp_schedule_events.append({
                                    'id': event_id,
                                    'title': f'{schedule.class_type.name if schedule.class_type else "N/A"} (Lớp lặp lại)',
                                    'start': start_datetime.isoformat(),
                                    'end': end_datetime.isoformat(),
                                    'color': schedule.calendar_color or '#3788d8',
                                    'extendedProps': {
                                        'type': 'recurring_class',
                                        'schedule_id': schedule.id,
                                        'class_name': schedule.class_type.name if schedule.class_type else 'N/A',
                                        'instructor_name': schedule.instructor.full_name if schedule.instructor else 'N/A',
                                        'room': schedule.room or 'N/A',
                                        'status': 'Lên lịch (Lặp lại)',
                                        'recurring_date': current_iter_date.isoformat()
                                    }
                                })
                                processed_schedule_ids.add(event_id)
                        current_iter_date += timedelta(days=1)
                        if len(temp_schedule_events) >= schedule_limit: break
                if len(temp_schedule_events) >= schedule_limit: 
                    print(f"Reached schedule_limit ({schedule_limit}) while processing schedules.")
                    break
            except Exception as e_schedule:
                print(f"Error processing schedule ID {schedule.id} (index {schedule_idx}): {str(e_schedule)}")
                continue
        events.extend(temp_schedule_events[:schedule_limit])
        print(f"Added {len(events)} schedule events.")

        print("Querying Appointments...")
        appointments = Appointment.objects.filter(
            appointment_date__gte=start_date.replace(hour=0, minute=0, second=0, microsecond=0),
            appointment_date__lt=(end_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        ).select_related('customer').prefetch_related('instructors').order_by('appointment_date')[:appointment_limit]
        print(f"Found {appointments.count()} appointments.")

        for appt_idx, appt in enumerate(appointments):
            print(f"Processing appointment ID {appt.id}")
            try:
                if not appt.appointment_date:
                    print(f"Skipping appointment ID {appt.id} due to missing appointment_date.")
                    continue
                appointment_start_dt = appt.appointment_date 
                appointment_end_dt = appt.appointment_date + timedelta(hours=1) 
                if appointment_end_dt <= start_date or appointment_start_dt >= end_date:
                    continue
                instructor_names = ", ".join([ins.full_name for ins in appt.instructors.all()]) if appt.instructors.exists() else 'N/A'
                customer_name = appt.customer.full_name if appt.customer else 'N/A'
                events.append({
                    'id': f'event_appointment_{appt.id}',
                    'title': f'Hẹn: {customer_name}' + (f' - {appt.service_name}' if hasattr(appt, 'service_name') and appt.service_name else ''),
                    'start': appointment_start_dt.isoformat(),
                    'end': appointment_end_dt.isoformat(),
                    'color': '#FF8C00',
                    'borderColor': '#FF8C00',
                    'extendedProps': {
                        'type': 'appointment',
                        'appointment_id': appt.id,
                        'customer_name': customer_name,
                        'instructor_names': instructor_names,
                        'notes': getattr(appt, 'notes', '') or '',
                    }
                })
            except Exception as e_appt:
                print(f"Error processing appointment ID {appt.id} (index {appt_idx}): {str(e_appt)}")
                continue
        print(f"Total events to return: {len(events)}")
        
        # print(f"Final events: {events}") # Có thể rất dài, chỉ bật nếu cần thiết
        # cache.set(cache_key, events, 300) # Tạm thời tắt cache
        return JsonResponse(events, safe=False)
        
    except Exception as e_main:
        print(f"CRITICAL ERROR in get_calendar_events: {str(e_main)}")
        import traceback # Quan trọng: Lấy traceback đầy đủ
        print(traceback.format_exc()) # IN TRACEBACK RA CONSOLE DJANGO
        return JsonResponse({'error': 'Lỗi máy chủ nghiêm trọng khi lấy dữ liệu lịch.', 'details': str(e_main)}, status=500)

@login_required
def class_schedule_calendar(request):
    today = date.today()
    
    # Lấy ngày từ GET params hoặc đặt giá trị mặc định
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    format_type = request.GET.get('format')  # Thêm tham số format để hỗ trợ JSON
    
    query_start_date = None
    query_end_date = None

    try:
        if start_date_str:
            query_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            query_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        # Nếu parse lỗi, quay về mặc định
        query_start_date = None
        query_end_date = None
        print("Lỗi parse ngày tháng từ GET params cho thống kê.")

    # Nếu không có ngày hợp lệ từ GET, đặt khoảng mặc định (ví dụ: tháng hiện tại)
    if not query_start_date or not query_end_date:
        query_start_date = today.replace(day=1)
        if today.month == 12:
            query_end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            query_end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        print(f"Không có GET params ngày hợp lệ, sử dụng khoảng mặc định cho thống kê: {query_start_date} to {query_end_date}")
    
    # Tạo bộ lọc cho truy vấn thống kê
    date_filter_kwargs = {
        'specific_date__gte': query_start_date,
        'specific_date__lte': query_end_date,
        'specific_date__isnull': False # Chỉ lấy các lịch có ngày cụ thể
    }

    # Thống kê lớp học
    class_stats = list(
        ClassSchedule.objects.filter(**date_filter_kwargs)
        .values('class_type__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Thống kê HLV
    instructor_stats = list(
        ClassSchedule.objects.filter(**date_filter_kwargs)
        .values('instructor__full_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Thống kê khung giờ
    time_stats = list(
        ClassSchedule.objects.filter(**date_filter_kwargs)
        .values('start_time', 'end_time')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Chuẩn bị dữ liệu
    data = {
        'class_stats': class_stats,
        'instructor_stats': instructor_stats,
        'time_stats': time_stats,
        'filter_start_date': query_start_date.strftime('%Y-%m-%d') if query_start_date else '',
        'filter_end_date': query_end_date.strftime('%Y-%m-%d') if query_end_date else '',
    }
    
    # Trả về JSON nếu format=json
    if format_type == 'json':
        return JsonResponse(data)
    
    # Mặc định trả về HTML template
    return render(request, 'dashboard/class_schedule_calendar.html', data)

@login_required
def delete_class_schedule(request, schedule_id):
    """API xóa ca học"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        schedule = ClassSchedule.objects.get(id=schedule_id)
        schedule.delete()
        
        # Xóa cache
        cache.delete_pattern('calendar_events:*')
        
        return JsonResponse({'message': 'Đã xóa ca học thành công'})
    except ClassSchedule.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy ca học'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_appointment(request, appointment_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.delete()
        # cache.delete_pattern(f'calendar_events:*:*:*')
        cache.clear() 
        return JsonResponse({'message': 'Đã xóa cuộc hẹn thành công'})
    except Exception as e:
        print(f"Error deleting appointment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def class_schedule_table(request):
    today = date.today()
    
    # Lấy tham số từ GET request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    instructor_id = request.GET.get('instructor')
    class_type_id = request.GET.get('class_type')
    status = request.GET.get('status')
    
    # Xử lý ngày mặc định: nếu không có tham số, lấy tháng hiện tại
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)  # Ngày đầu tháng
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            # Ngày cuối tháng
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    except ValueError:
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Tạo filter cho query
    filters = Q(specific_date__gte=start_date, specific_date__lte=end_date)
    
    # Thêm các filter tùy chọn
    if instructor_id:
        filters &= Q(instructor_id=instructor_id)
    
    if class_type_id:
        filters &= Q(class_type_id=class_type_id)
    
    if status:
        filters &= Q(status=status)
    
    # Lấy danh sách lịch học
    schedules = ClassSchedule.objects.filter(
        filters
    ).select_related('class_type', 'instructor').order_by('specific_date', 'start_time')
    
    # Phân trang
    page = request.GET.get('page', 1)
    paginator = Paginator(schedules, 20)  # 20 lịch học mỗi trang
    
    try:
        schedules_page = paginator.page(page)
    except PageNotAnInteger:
        schedules_page = paginator.page(1)
    except EmptyPage:
        schedules_page = paginator.page(paginator.num_pages)
    
    # Lấy danh sách huấn luyện viên và loại lớp học để hiển thị trong bộ lọc
    instructors = Instructor.objects.all().order_by('full_name')
    class_types = ClassType.objects.all().order_by('name')
    
    context = {
        'schedules': schedules_page,
        'instructors': instructors,
        'class_types': class_types,
        'start_date': start_date,
        'end_date': end_date,
        'selected_instructor': int(instructor_id) if instructor_id and instructor_id.isdigit() else None,
        'selected_class_type': int(class_type_id) if class_type_id and class_type_id.isdigit() else None,
        'selected_status': status
    }
    
    return render(request, 'dashboard/class_schedule_table.html', context)

@login_required
def class_schedule_form(request):
    """View để xử lý form đăng ký lịch học với giao diện mới"""
    from instructors.models import Instructor
    from customers.models import Customer, CustomerPackage
    from branches.models import Branch
    
    # Lấy danh sách dữ liệu cần thiết
    instructors = Instructor.objects.all().order_by('full_name')
    class_types = ClassType.objects.all().order_by('name')
    customers = Customer.objects.filter(status__in=['purchased', 'repurchased']).order_by('full_name')
    branches = Branch.objects.all().order_by('name')
    
    # Danh sách thứ trong tuần để chọn lặp lại
    weekdays = [
        (0, 'Thứ 2'),
        (1, 'Thứ 3'),
        (2, 'Thứ 4'),
        (3, 'Thứ 5'),
        (4, 'Thứ 6'),
        (5, 'Thứ 7'),
        (6, 'Chủ nhật'),
    ]
    
    # Xử lý POST request
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            class_type_id = request.POST.get('class_type')
            instructor_id = request.POST.get('instructor')
            branch_id = request.POST.get('branch')
            room = request.POST.get('room')
            start_date_str = request.POST.get('start_date')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            is_recurring = request.POST.get('is_recurring') == 'on'
            recurring_days = request.POST.getlist('recurring_days')
            customer_id = request.POST.get('customer')
            num_sessions = request.POST.get('num_sessions')
            notes = request.POST.get('notes')
            
            # Chuyển đổi dữ liệu
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            recurring_days = [int(day) for day in recurring_days] if recurring_days else []
            
            if is_recurring and recurring_days:
                # Tạo lịch học lặp lại
                schedule = ClassSchedule(
                    class_type_id=class_type_id,
                    instructor_id=instructor_id,
                    branch_id=branch_id,
                    room=room,
                    start_date=start_date,
                    start_time=start_time,
                    end_time=end_time,
                    is_recurring=True,
                    recurring_days=recurring_days,
                    status='scheduled',
                    notes=notes
                )
                schedule.save()
                
                # Nếu chọn khách hàng, tạo các buổi học cho khách hàng đó
                if customer_id and num_sessions and int(num_sessions) > 0:
                    customer = Customer.objects.get(id=customer_id)
                    # Xử lý việc tạo các buổi học cho khách hàng
                    # Đây là phần mở rộng cần bổ sung thêm
                
                return redirect('dashboard:class_schedule_calendar')
            else:
                # Tạo lịch học đơn lẻ
                schedule = ClassSchedule(
                    class_type_id=class_type_id,
                    instructor_id=instructor_id,
                    branch_id=branch_id,
                    room=room,
                    specific_date=start_date,
                    start_time=start_time,
                    end_time=end_time,
                    is_recurring=False,
                    status='scheduled',
                    notes=notes
                )
                schedule.save()
                
                # Nếu chọn khách hàng, tạo buổi học cho khách hàng đó
                if customer_id:
                    customer = Customer.objects.get(id=customer_id)
                    # Xử lý việc tạo buổi học cho khách hàng
                    # Đây là phần mở rộng cần bổ sung thêm
                
                return redirect('dashboard:class_schedule_calendar')
                
        except Exception as e:
            # Xử lý lỗi
            error_message = str(e)
            context = {
                'error_message': error_message,
                'instructors': instructors,
                'class_types': class_types,
                'customers': customers,
                'branches': branches,
                'weekdays': weekdays,
                'form_data': request.POST  # Giữ lại dữ liệu đã nhập
            }
            return render(request, 'dashboard/class_schedule_form.html', context)
    
    # GET request, hiển thị form
    context = {
        'instructors': instructors,
        'class_types': class_types,
        'customers': customers,
        'branches': branches,
        'weekdays': weekdays
    }
    
    return render(request, 'dashboard/class_schedule_form.html', context)

@login_required
def package_list(request):
    """Hiển thị danh sách các gói tập"""
    # Lấy tham số tìm kiếm và lọc
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    class_type_filter = request.GET.get('class_type', '')
    
    # Truy vấn cơ bản
    packages = CustomerPackage.objects.all().select_related('customer', 'class_type')
    
    # Áp dụng các bộ lọc
    if search_query:
        packages = packages.filter(
            Q(customer__full_name__icontains=search_query) |
            Q(class_type__name__icontains=search_query)
        )
    
    if status_filter:
        packages = packages.filter(status=status_filter)
        
    if class_type_filter:
        packages = packages.filter(class_type_id=class_type_filter)
    
    # Sắp xếp theo ngày mua gần nhất
    packages = packages.order_by('-purchase_date')
    
    # Phân trang
    paginator = Paginator(packages, 20)  # 20 gói mỗi trang
    page = request.GET.get('page')
    try:
        packages = paginator.page(page)
    except PageNotAnInteger:
        packages = paginator.page(1)
    except EmptyPage:
        packages = paginator.page(paginator.num_pages)
    
    # Lấy danh sách loại lớp cho bộ lọc
    class_types = ClassType.objects.all()
    
    context = {
        'packages': packages,
        'class_types': class_types,
        'search_query': search_query,
        'status_filter': status_filter,
        'class_type_filter': class_type_filter,
        'statuses': CustomerPackage.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/package_list.html', context)

@login_required
def package_form(request, pk=None):
    """Form thêm mới hoặc chỉnh sửa gói tập"""
    package = None
    form_title = "Thêm gói tập mới"
    
    if pk:
        package = get_object_or_404(CustomerPackage, pk=pk)
        form_title = f"Chỉnh sửa gói tập: {package}"
    else:
        # Tạo một đối tượng package tạm thời để tránh lỗi None
        package = CustomerPackage(
            total_sessions=10,
            remaining_sessions=10,
            status='active',
            start_date=datetime.now().date()
        )
    
    if request.method == 'POST':
        # Xử lý form khi submit
        customer_id = request.POST.get('customer')
        payment_id = request.POST.get('payment')
        class_type_id = request.POST.get('class_type')
        total_sessions = request.POST.get('total_sessions')
        remaining_sessions = request.POST.get('remaining_sessions')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        try:
            customer = Customer.objects.get(id=customer_id)
            class_type = ClassType.objects.get(id=class_type_id)
            
            # Lấy đơn hàng nếu có
            payment = None
            if payment_id:
                from payments.models import Payment
                payment = Payment.objects.get(id=payment_id)
            
            # Chuyển đổi dữ liệu
            total_sessions = int(total_sessions)
            remaining_sessions = int(remaining_sessions)
            
            # Xử lý ngày với định dạng yyyy-mm-dd từ HTML5 input type="date"
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.now().date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            except ValueError as e:
                # Xử lý lỗi nếu định dạng ngày không hợp lệ
                print(f"Lỗi định dạng ngày: {str(e)}")
                start_date = datetime.now().date()
                end_date = None
            
            # Nếu là cập nhật
            if pk:
                package.customer = customer
                package.class_type = class_type
                package.payment = payment
                package.total_sessions = total_sessions
                package.remaining_sessions = remaining_sessions
                package.start_date = start_date
                package.end_date = end_date
                package.status = status
                package.notes = notes
                package.save()
                return redirect('dashboard:package_list')
            else:
                # Tạo mới gói
                new_package = CustomerPackage(
                    customer=customer,
                    class_type=class_type,
                    payment=payment,
                    total_sessions=total_sessions,
                    remaining_sessions=remaining_sessions,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    notes=notes
                )
                new_package.save()
                return redirect('dashboard:package_list')
                
        except (Customer.DoesNotExist, ClassType.DoesNotExist, ValueError) as e:
            # Xử lý lỗi
            error_message = f"Lỗi khi lưu gói tập: {str(e)}"
            # Truyền lỗi vào context và hiển thị lại form
            context = {
                'package': package,
                'customers': Customer.objects.all(),
                'class_types': ClassType.objects.all(),
                'statuses': CustomerPackage.STATUS_CHOICES,
                'form_title': form_title,
                'error_message': error_message,
                'pk': pk
            }
            return render(request, 'dashboard/package_form.html', context)
    
    # Hiển thị form
    # Lấy danh sách đơn hàng
    from payments.models import Payment
    payments = Payment.objects.all().order_by('-payment_date')
    
    context = {
        'package': package,
        'customers': Customer.objects.all(),
        'class_types': ClassType.objects.all(),
        'statuses': CustomerPackage.STATUS_CHOICES,
        'form_title': form_title,
        'pk': pk,
        'payments': payments
    }
    return render(request, 'dashboard/package_form.html', context)

@login_required
def package_delete(request, pk):
    """Xóa gói tập"""
    package = get_object_or_404(CustomerPackage, pk=pk)
    
    if request.method == 'POST':
        package.delete()
        return redirect('dashboard:package_list')
    
    context = {
        'package': package
    }
    return render(request, 'dashboard/package_delete.html', context)

@login_required
def payment_redirect(request):
    """Chuyển hướng đến module đơn hàng"""
    return redirect('payment_list')

@login_required
def customer_add_view(request):
    """Thêm mới khách hàng"""
    
    # Lấy danh sách chi nhánh
    branches = Branch.objects.all()
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        birthday = request.POST.get('birthday')
        address = request.POST.get('address')
        facebook = request.POST.get('facebook')
        branch_id = request.POST.get('branch')
        health_notes = request.POST.get('health_notes')
        notes = request.POST.get('notes')
        status = request.POST.get('status', 'contact')  # Mặc định là 'contact'
        gender = request.POST.get('gender', 'M')  # Mặc định là Nam
        parent_id = request.POST.get('parent')
        parent_name = request.POST.get('parent_name')
        parent_phone = request.POST.get('parent_phone')
        emergency_contact = request.POST.get('emergency_contact')
        source = request.POST.get('source', 'direct')  # Mặc định là 'direct'
        
        # Tạo khách hàng mới
        customer = Customer(
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            health_issues=health_notes,
            notes=notes,
            status=status,
            gender=gender,
            parent_id=parent_id,
            parent_name=parent_name,
            parent_phone=parent_phone,
            emergency_contact=emergency_contact,
            source=source
        )
        
        # Xử lý ngày sinh nếu có
        if birthday:
            try:
                customer.date_of_birth = datetime.strptime(birthday, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Xử lý chi nhánh nếu có
        if branch_id:
            try:
                customer.branch_id = int(branch_id)
            except ValueError:
                pass
        
        customer.save()
        return redirect('dashboard:customer_detail', pk=customer.id)
    
    return render(request, 'dashboard/customer_add.html', {
        'branches': branches,
        'customers': Customer.objects.filter(active=True),  # Thêm danh sách khách hàng để chọn làm bố/mẹ
    })

@login_required
def instructor_list(request):
    """Hiển thị danh sách huấn luyện viên"""
    instructors = Instructor.objects.all().order_by('full_name')
    
    context = {
        'instructors': instructors,
        'title': 'Danh sách huấn luyện viên'
    }
    
    return render(request, 'dashboard/instructor_list.html', context)

@login_required
def classtype_list(request):
    """Hiển thị danh sách các loại lớp học"""
    class_types = ClassType.objects.all().order_by('name')
    
    # Tìm kiếm
    search_query = request.GET.get('q', '')
    if search_query:
        class_types = class_types.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Phân trang
    paginator = Paginator(class_types, 20)  # 20 loại lớp học mỗi trang
    page = request.GET.get('page')
    try:
        class_types = paginator.page(page)
    except PageNotAnInteger:
        class_types = paginator.page(1)
    except EmptyPage:
        class_types = paginator.page(paginator.num_pages)
    
    context = {
        'class_types': class_types,
        'search_query': search_query,
        'title': 'Danh sách loại lớp học'
    }
    
    return render(request, 'dashboard/classtype_list.html', context)

@login_required
def branch_list(request):
    """Hiển thị danh sách chi nhánh"""
    branches = Branch.objects.all().order_by('name')
    
    # Tìm kiếm
    search_query = request.GET.get('q', '')
    if search_query:
        branches = branches.filter(name__icontains=search_query)
    
    # Phân trang
    paginator = Paginator(branches, 20)
    page = request.GET.get('page')
    try:
        branches = paginator.page(page)
    except PageNotAnInteger:
        branches = paginator.page(1)
    except EmptyPage:
        branches = paginator.page(paginator.num_pages)
    
    context = {
        'branches': branches,
        'search_query': search_query,
        'title': 'Danh sách chi nhánh'
    }
    
    return render(request, 'dashboard/branch_list.html', context)

@login_required
def user_list(request):
    """Hiển thị danh sách người dùng hệ thống"""
    users = User.objects.all().order_by('username')
    
    # Tìm kiếm
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Phân trang
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'search_query': search_query,
        'title': 'Danh sách người dùng'
    }
    
    return render(request, 'dashboard/user_list.html', context)

@login_required
def customer_list(request):
    """View hiển thị danh sách khách hàng"""
    # Lấy tham số tìm kiếm
    search_query = request.GET.get('search', '')
    
    # Truy vấn danh sách khách hàng
    customers = Customer.objects.all().order_by('-registration_date')
    
    # Lọc theo từ khóa tìm kiếm
    if search_query:
        customers = customers.filter(
            Q(full_name__icontains=search_query) | 
            Q(phone__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    # Phân trang
    paginator = Paginator(customers, 20)  # 20 khách hàng mỗi trang
    page = request.GET.get('page')
    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        customers_page = paginator.page(1)
    except EmptyPage:
        customers_page = paginator.page(paginator.num_pages)
    
    # Chuẩn bị context
    context = {
        'customers': customers_page,
        'search_query': search_query,
        'title': 'Danh sách khách hàng'
    }
    
    return render(request, 'dashboard/customer_list.html', context)

@login_required
def search_customers_api(request):
    """API endpoint tìm kiếm khách hàng cho autocomplete"""
    search_term = request.GET.get('q', '')
    if not search_term or len(search_term) < 2:
        return JsonResponse([], safe=False)
    
    customers = Customer.objects.filter(
        Q(full_name__icontains=search_term) | 
        Q(phone__icontains=search_term)
    )[:10]  # Giới hạn kết quả để tránh quá tải
    
    results = []
    for customer in customers:
        results.append({
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone or ''
        })
    
    return JsonResponse(results, safe=False)

@login_required
def search_customers(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    print(f"Tìm kiếm khách hàng với query: {query}")
    
    customers = Customer.objects.filter(
        Q(full_name__icontains=query) | 
        Q(phone__icontains=query)
    ).filter(active=True)[:10]
    
    print(f"Tìm thấy {customers.count()} khách hàng")
    
    results = []
    for c in customers:
        # Kết quả hiển thị cho select2
        customer_data = {
            'id': c.id,
            'text': f"{c.full_name} - {c.phone or 'Không có SĐT'}",
            # Thông tin để điền vào form
            'name': c.full_name,
            'phone': c.phone or ''
        }
        results.append(customer_data)
    
    print(f"Kết quả trả về: {results}")
    
    return JsonResponse({'results': results})
