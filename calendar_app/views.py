from django.shortcuts import render
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from classes.models import ClassSchedule, ClassType
from customers.models import Appointment, Customer
from instructors.models import Instructor
from datetime import datetime, timedelta
import json
import random

@method_decorator(login_required, name='dispatch')
class CalendarView(TemplateView):
    template_name = 'calendar/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def get_calendar_events(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    view_type = request.GET.get('view_type', 'month')  # month, week, day
    
    # Chuyển đổi chuỗi ngày thành đối tượng datetime
    try:
        if start_date:
            # Xử lý tất cả các trường hợp có thể xảy ra với chuỗi thời gian
            start_date = start_date.replace(' ', '+')
            
            # Trường hợp có dấu cách giữa thời gian và múi giờ
            if ' ' in start_date:
                start_date = start_date.replace(' ', '+')
            
            # Xử lý trường hợp định dạng không đúng của múi giờ
            if '+' in start_date:
                parts = start_date.split('+')
                base_date = parts[0]
                # Nếu phần offset không có ':'
                if len(parts) > 1 and ':' not in parts[1]:
                    offset = parts[1]
                    if len(offset) >= 2:
                        # Định dạng lại offset thành HH:MM
                        formatted_offset = offset[:2]
                        if len(offset) > 2:
                            formatted_offset += ':' + offset[2:4]
                        else:
                            formatted_offset += ':00'
                        start_date = base_date + '+' + formatted_offset
                
            # Xử lý trường hợp không có múi giờ
            if 'Z' in start_date:
                start_date = start_date.replace('Z', '+00:00')
            
            # Xử lý bất kỳ định dạng nào khác
            try:
                start_date = datetime.fromisoformat(start_date)
            except ValueError:
                print(f"Lỗi định dạng thời gian start_date: {start_date}")
                # Thử cách khác - loại bỏ timezone
                if '+' in start_date:
                    start_date = start_date.split('+')[0]
                    start_date = datetime.fromisoformat(start_date)
                else:
                    # Mặc định là ngày hiện tại
                    start_date = datetime.now()
        else:
            start_date = datetime.now()
        
        # Tương tự cho end_date
        if end_date:
            end_date = end_date.replace(' ', '+')
            
            if ' ' in end_date:
                end_date = end_date.replace(' ', '+')
            
            if '+' in end_date:
                parts = end_date.split('+')
                base_date = parts[0]
                if len(parts) > 1 and ':' not in parts[1]:
                    offset = parts[1]
                    if len(offset) >= 2:
                        formatted_offset = offset[:2]
                        if len(offset) > 2:
                            formatted_offset += ':' + offset[2:4]
                        else:
                            formatted_offset += ':00'
                        end_date = base_date + '+' + formatted_offset
            
            if 'Z' in end_date:
                end_date = end_date.replace('Z', '+00:00')
            
            try:
                end_date = datetime.fromisoformat(end_date)
            except ValueError:
                print(f"Lỗi định dạng thời gian end_date: {end_date}")
                if '+' in end_date:
                    end_date = end_date.split('+')[0]
                    end_date = datetime.fromisoformat(end_date)
                else:
                    # Mặc định là start_date + 30 ngày
                    end_date = start_date + timedelta(days=30)
        else:
            end_date = start_date + timedelta(days=30)
    except Exception as e:
        # Log lỗi để debug
        print(f"Lỗi xử lý thời gian: {e}, start_date={start_date}, end_date={end_date}")
        # Nếu có lỗi, sử dụng ngày hiện tại và thêm 1 tháng
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
    
    events = []
    
    # Lấy tất cả lịch học cố định trong khoảng thời gian
    schedules = ClassSchedule.objects.filter(
        Q(specific_date__isnull=False, specific_date__gte=start_date.date(), specific_date__lte=end_date.date()) |
        Q(is_recurring=True, start_date__lte=end_date.date()) &
        (Q(end_date__isnull=True) | Q(end_date__gte=start_date.date()))
    ).select_related('class_type', 'instructor')
    
    # Tạo events từ các lịch học cụ thể
    for schedule in schedules:
        if schedule.specific_date:
            # Đây là buổi học cụ thể đã được tạo
            start_datetime = datetime.combine(schedule.specific_date, schedule.start_time)
            end_datetime = datetime.combine(schedule.specific_date, schedule.end_time)
            
            event = {
                'id': f'class_{schedule.id}',
                'title': f'{schedule.class_type.name} - {schedule.instructor.full_name}',
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'color': schedule.calendar_color,
                'url': f'/admin/classes/classschedule/{schedule.id}/change/',
                'extendedProps': {
                    'status': schedule.status,
                    'room': schedule.room,
                    'type': 'class',
                    'instructor': schedule.instructor.full_name
                }
            }
            events.append(event)
        elif schedule.is_recurring:
            # Đây là lịch lặp lại, cần tạo các sự kiện cụ thể
            recurring_days = schedule.recurring_days or [schedule.day_of_week]
            
            # Tạo các buổi học cho tất cả các ngày lặp lại trong khoảng thời gian
            current_date = max(schedule.start_date, start_date.date())
            end_limit = min(end_date.date(), schedule.end_date or end_date.date())
            
            while current_date <= end_limit:
                weekday = current_date.weekday()
                
                # Nếu ngày hiện tại là một trong các ngày lặp lại
                if weekday in recurring_days:
                    # Kiểm tra xem đã có buổi học cụ thể cho ngày này chưa
                    existing = ClassSchedule.objects.filter(
                        parent_schedule=schedule,
                        specific_date=current_date
                    ).first()
                    
                    # Nếu không có, tạo event từ lịch lặp lại
                    if not existing:
                        start_datetime = datetime.combine(current_date, schedule.start_time)
                        end_datetime = datetime.combine(current_date, schedule.end_time)
                        
                        event = {
                            'id': f'recurring_{schedule.id}_{current_date.isoformat()}',
                            'title': f'{schedule.class_type.name} - {schedule.instructor.full_name}',
                            'start': start_datetime.isoformat(),
                            'end': end_datetime.isoformat(),
                            'color': schedule.calendar_color,
                            'url': f'/admin/classes/classschedule/{schedule.id}/change/',
                            'extendedProps': {
                                'status': 'scheduled',
                                'room': schedule.room,
                                'type': 'recurring_class',
                                'instructor': schedule.instructor.full_name
                            }
                        }
                        events.append(event)
                
                current_date += timedelta(days=1)
    
    # Lấy tất cả các cuộc hẹn trong khoảng thời gian
    appointments = Appointment.objects.filter(
        appointment_date__gte=start_date,
        appointment_date__lte=end_date
    ).select_related('customer').prefetch_related('instructors')
    
    # Tạo events từ các cuộc hẹn
    for appointment in appointments:
        start_datetime = appointment.appointment_date
        # Cuộc hẹn kéo dài 1 giờ mặc định nếu không có thông tin thời gian kết thúc
        end_datetime = start_datetime + timedelta(hours=1)
        
        instructor_names = ", ".join([instructor.full_name for instructor in appointment.instructors.all()])
        
        event = {
            'id': f'appointment_{appointment.id}',
            'title': f'Hẹn: {appointment.customer.full_name}',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'color': '#FF5722',  # Màu cam cho cuộc hẹn
            'url': f'/admin/customers/appointment/{appointment.id}/change/',
            'extendedProps': {
                'type': 'appointment',
                'customer': appointment.customer.full_name,
                'instructor': instructor_names,
                'content': appointment.content
            }
        }
        events.append(event)
    
    return JsonResponse(events, safe=False)

@login_required
def get_statistics(request):
    """Trả về thống kê theo khoảng thời gian"""
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # Chuyển đổi chuỗi ngày thành đối tượng datetime (sử dụng logic giống get_calendar_events)
    try:
        if start_date:
            # Xử lý tất cả các trường hợp có thể xảy ra với chuỗi thời gian
            start_date = start_date.replace(' ', '+')
            
            # Trường hợp có dấu cách giữa thời gian và múi giờ
            if ' ' in start_date:
                start_date = start_date.replace(' ', '+')
            
            # Xử lý trường hợp định dạng không đúng của múi giờ
            if '+' in start_date:
                parts = start_date.split('+')
                base_date = parts[0]
                # Nếu phần offset không có ':'
                if len(parts) > 1 and ':' not in parts[1]:
                    offset = parts[1]
                    if len(offset) >= 2:
                        # Định dạng lại offset thành HH:MM
                        formatted_offset = offset[:2]
                        if len(offset) > 2:
                            formatted_offset += ':' + offset[2:4]
                        else:
                            formatted_offset += ':00'
                        start_date = base_date + '+' + formatted_offset
                
            # Xử lý trường hợp không có múi giờ
            if 'Z' in start_date:
                start_date = start_date.replace('Z', '+00:00')
            
            # Xử lý bất kỳ định dạng nào khác
            try:
                start_date = datetime.fromisoformat(start_date).date()
            except ValueError:
                print(f"Lỗi định dạng thời gian start_date: {start_date}")
                # Thử cách khác - loại bỏ timezone
                if '+' in start_date:
                    start_date = start_date.split('+')[0]
                    start_date = datetime.fromisoformat(start_date).date()
                else:
                    # Mặc định là ngày hiện tại
                    start_date = datetime.now().date()
        else:
            start_date = datetime.now().date()
        
        # Tương tự cho end_date
        if end_date:
            end_date = end_date.replace(' ', '+')
            
            if ' ' in end_date:
                end_date = end_date.replace(' ', '+')
            
            if '+' in end_date:
                parts = end_date.split('+')
                base_date = parts[0]
                if len(parts) > 1 and ':' not in parts[1]:
                    offset = parts[1]
                    if len(offset) >= 2:
                        formatted_offset = offset[:2]
                        if len(offset) > 2:
                            formatted_offset += ':' + offset[2:4]
                        else:
                            formatted_offset += ':00'
                        end_date = base_date + '+' + formatted_offset
            
            if 'Z' in end_date:
                end_date = end_date.replace('Z', '+00:00')
            
            try:
                end_date = datetime.fromisoformat(end_date).date()
            except ValueError:
                print(f"Lỗi định dạng thời gian end_date: {end_date}")
                if '+' in end_date:
                    end_date = end_date.split('+')[0]
                    end_date = datetime.fromisoformat(end_date).date()
                else:
                    # Mặc định là start_date + 30 ngày
                    end_date = (datetime.now() + timedelta(days=30)).date()
        else:
            end_date = (datetime.now() + timedelta(days=30)).date()
    except Exception as e:
        # Log lỗi để debug
        print(f"Lỗi xử lý thời gian trong statistics: {e}, start_date={start_date}, end_date={end_date}")
        # Nếu có lỗi, sử dụng ngày hiện tại và thêm 1 tháng
        start_date = datetime.now().date()
        end_date = (datetime.now() + timedelta(days=30)).date()
    
    # Thống kê loại lớp học
    class_type_stats = ClassSchedule.objects.filter(
        specific_date__gte=start_date,
        specific_date__lt=end_date
    ).values('class_type__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Chuyển đổi QuerySet thành list để dễ xử lý
    class_type_stats = list(class_type_stats)
    
    # Thống kê huấn luyện viên
    instructor_stats = ClassSchedule.objects.filter(
        specific_date__gte=start_date,
        specific_date__lt=end_date
    ).values('instructor__full_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Chuyển đổi QuerySet thành list để dễ xử lý
    instructor_stats = list(instructor_stats)
    
    # Thống kê cuộc hẹn
    appointment_count = Appointment.objects.filter(
        appointment_date__date__gte=start_date,
        appointment_date__date__lte=end_date
    ).count()
    
    # Chuyển đổi dữ liệu sang định dạng mới nhất quán
    class_types_data = [{
        'name': stat['class_type__name'],
        'count': stat['count']
    } for stat in class_type_stats]
    
    instructors_data = [{
        'name': stat['instructor__full_name'],
        'count': stat['count']
    } for stat in instructor_stats]
    
    # Chuẩn bị dữ liệu trả về
    data = {
        'class_types': class_types_data,
        'instructors': instructors_data,
        'appointment_count': appointment_count
    }
    
    return JsonResponse(data)

@login_required
def get_class_types(request):
    """API endpoint để lấy danh sách loại lớp học"""
    class_types = ClassType.objects.all().values('id', 'name')
    return JsonResponse(list(class_types), safe=False)

@login_required
def get_instructors(request):
    """API endpoint để lấy danh sách huấn luyện viên"""
    instructors = Instructor.objects.all().values('id', 'full_name')
    return JsonResponse(list(instructors), safe=False)

@login_required
def get_customers(request):
    """Trả về danh sách khách hàng theo tìm kiếm"""
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(
        Q(full_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(email__icontains=query)
    ).values('id', 'full_name', 'phone', 'email')[:20]
    
    results = []
    for customer in customers:
        results.append({
            'id': customer['id'],
            'text': f"{customer['full_name']} - {customer['phone']}",
            'name': customer['full_name'],
            'phone': customer['phone'],
            'email': customer['email']
        })
    
    if not query:
        # Nếu không có query, trả về tất cả khách hàng (giới hạn 50 người)
        all_customers = Customer.objects.all().values('id', 'full_name', 'phone', 'email')[:50]
        for customer in all_customers:
            if not any(r['id'] == customer['id'] for r in results):
                results.append({
                    'id': customer['id'],
                    'text': f"{customer['full_name']} - {customer['phone']}",
                    'name': customer['full_name'],
                    'phone': customer['phone'],
                    'email': customer['email']
                })
    
    return JsonResponse({'results': results}, safe=False)
