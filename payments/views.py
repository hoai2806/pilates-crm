from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
import os
from django.views.decorators.http import require_POST

# Thêm hàm để xử lý chuỗi tiền tệ
def clean_currency(value):
    if isinstance(value, str):
        # Loại bỏ dấu chấm phân cách hàng nghìn, ký hiệu tiền tệ và dấu %
        value = value.replace('.', '').replace(' VNĐ', '').replace(',', '.').replace('%', '')
    return float(value)

from .models import Payment, Expense
from customers.models import Customer, CustomerPackage
from classes.models import ClassType, ClassTypePrice
from instructors.models import Instructor
from branches.models import Branch

@login_required
def payment_list(request):
    """Hiển thị danh sách đơn hàng"""
    payments = Payment.objects.select_related('customer', 'class_type', 'branch').order_by('-payment_date')
    
    # Tìm kiếm và lọc
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    branch_id = request.GET.get('branch')
    
    if search_query:
        payments = payments.filter(
            customer__full_name__icontains=search_query
        ) | payments.filter(
            invoice_number__icontains=search_query
        )
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Lọc theo ngày
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__lte=date_to)
        except ValueError:
            pass
    
    if branch_id:
        payments = payments.filter(branch_id=branch_id)
    
    # Tính tổng doanh thu cho kết quả tìm kiếm
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Tổng doanh thu đã nhận
    total_received = payments.aggregate(total=Sum('paid_amount'))['total'] or 0
    
    # Tổng tiền còn nợ
    total_debt = payments.aggregate(total=Sum('remaining_amount'))['total'] or 0
    
    # Tổng số đơn hàng
    total_orders = payments.count()
    
    # Gói doanh thu cao nhất
    top_package = (
        payments.values('class_type__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )
    top_package_name = top_package['class_type__name'] if top_package else ''
    top_package_total = top_package['total'] if top_package else 0
    
    # Danh sách chi nhánh
    branches = Branch.objects.all()
    # Phân tích doanh thu theo từng chi nhánh
    branch_stats = []
    for branch in branches:
        branch_payments = Payment.objects.filter(branch=branch)
        branch_stats.append({
            'name': branch.name,
            'total': branch_payments.aggregate(total=Sum('amount'))['total'] or 0,
            'received': branch_payments.aggregate(total=Sum('paid_amount'))['total'] or 0,
            'debt': branch_payments.aggregate(total=Sum('remaining_amount'))['total'] or 0,
            'count': branch_payments.count(),
        })
    
    context = {
        'payments': payments,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'total_received': total_received,
        'total_debt': total_debt,
        'total_orders': total_orders,
        'top_package_name': top_package_name,
        'top_package_total': top_package_total,
        'branches': branches,
        'selected_branch': int(branch_id) if branch_id else None,
        'branch_stats': branch_stats,
        'statuses': Payment.STATUS_CHOICES,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    
    return render(request, 'payments/payment_list.html', context)

@login_required
def payment_detail(request, pk):
    """Hiển thị chi tiết đơn hàng"""
    payment = get_object_or_404(Payment, id=pk)
    
    # Lấy các gói tập liên quan
    customer_packages = CustomerPackage.objects.filter(payment=payment)
    
    context = {
        'payment': payment,
        'customer_packages': customer_packages,
    }
    
    return render(request, 'payments/payment_detail.html', context)

@login_required
def payment_create(request):
    """Tạo đơn hàng mới"""
    customers = Customer.objects.all().order_by('full_name')
    class_types = ClassType.objects.all().order_by('name')
    instructors = Instructor.objects.filter(active=True).order_by('full_name')
    branches = Branch.objects.filter(active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            print("Xử lý POST request tạo đơn hàng mới")
            # Lấy dữ liệu từ form với tên input mới
            customer_id = request.POST.get('customer')
            class_type_id = request.POST.get('class_type')
            class_price_id = request.POST.get('class_price')
            amount_value = request.POST.get('payment_amount_value') or request.POST.get('amount_value') or '0'
            paid_amount = request.POST.get('paid_amount_value') or '0'
            discount_type = request.POST.get('discount_type')
            discount_percentage = request.POST.get('discount_percentage', '0')
            discount_amount_value = request.POST.get('discount_amount', '0')
            bonus_sessions = request.POST.get('bonus_sessions', '0')
            payment_type = request.POST.get('payment_type', 'full')
            remaining_payment_due_date = request.POST.get('remaining_payment_due_date')
            payment_method = request.POST.get('payment_method')
            payment_date = request.POST.get('payment_date')
            status = request.POST.get('status')
            notes = request.POST.get('notes')
            payment_proof = request.FILES.get('payment_proof')
            instructor_id = request.POST.get('instructor')
            instructor = Instructor.objects.get(id=instructor_id) if instructor_id else None
            branch_id = request.POST.get('branch')
            branch = Branch.objects.get(id=branch_id) if branch_id else None

            # Lấy thông tin khách hàng và gói tập
            customer = Customer.objects.get(id=customer_id)
            class_price = ClassTypePrice.objects.get(id=class_price_id)
            class_type = ClassType.objects.get(id=class_type_id)

            # Parse số tiền từ hidden field
            try:
                amount_value = float(str(amount_value).replace('.', '').replace(',', ''))
            except (ValueError, TypeError):
                print(f"Lỗi parse giá trị amount_value: {amount_value}")
                amount_value = 0
            try:
                paid_amount = float(str(paid_amount).replace('.', '').replace(',', ''))
            except (ValueError, TypeError):
                paid_amount = 0

            # Tính giảm giá
            discount = 0
            discount_val = 0
            if discount_type == 'percentage':
                discount_val = float(str(discount_percentage).replace('%','').replace(',','').replace('.',''))
                discount = int(amount_value * discount_val / 100)
            elif discount_type == 'amount':
                discount_val = float(str(discount_amount_value).replace('.', '').replace(',', ''))
                discount = int(discount_val)
            final_amount = int(amount_value - discount)
            if final_amount < 0:
                final_amount = 0

            # Tính số tiền còn lại
            if payment_type == 'partial':
                if paid_amount > final_amount:
                    paid_amount = final_amount
                remaining_amount = final_amount - paid_amount
                if remaining_amount < 0:
                    remaining_amount = 0
            else:
                paid_amount = final_amount
                remaining_amount = 0

            # Tạo đơn hàng mới
            payment = Payment.objects.create(
                customer=customer,
                amount=amount_value,
                payment_method=payment_method,
                payment_date=payment_date,
                status=status,
                notes=notes,
                class_type=class_type,
                payment_type=payment_type,
                instructor=instructor,
                branch=branch,
                discount_type=discount_type,
                discount_value=discount_val,
                paid_amount=paid_amount,
                remaining_amount=remaining_amount,
                remaining_payment_due_date=remaining_payment_due_date if payment_type == 'partial' else None,
            )

            # Lưu file chứng từ thanh toán nếu có
            if payment_proof:
                upload_dir = f'payment_proofs/{timezone.now().strftime("%Y/%m/%d")}'
                if not os.path.exists(f'media/{upload_dir}'):
                    os.makedirs(f'media/{upload_dir}', exist_ok=True)
                filename = f"{customer.id}_{timezone.now().strftime('%H%M%S')}_{payment_proof.name}"
                file_path = f'{upload_dir}/{filename}'
                with open(f'media/{file_path}', 'wb+') as destination:
                    for chunk in payment_proof.chunks():
                        destination.write(chunk)
                payment.payment_proof = file_path
                payment.save()

            # Tạo gói tập mới cho khách hàng
            regular_sessions = class_price.number_of_sessions
            total_sessions = regular_sessions + int(bonus_sessions)
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=90)
            customer_package = CustomerPackage.objects.create(
                customer=customer,
                class_type=class_type,
                total_sessions=total_sessions,
                remaining_sessions=total_sessions,
                start_date=start_date,
                end_date=end_date,
                status='active',
                payment=payment
            )
            messages.success(request, f'Đã tạo đơn hàng và gói tập mới cho khách hàng {customer.full_name}')
            return redirect('payment_detail', pk=payment.id)
            
        except Exception as e:
            import traceback
            print(f"Error in payment_create: {str(e)}")
            traceback.print_exc()
            messages.error(request, f'Lỗi: {str(e)}')
    
    context = {
        'customers': customers,
        'class_types': class_types,
        'today_date': timezone.now(),
        'payment_types': Payment.PAYMENT_TYPE_CHOICES,
        'instructors': instructors,
        'branches': branches,
        'payment': None,
        'paid_amount': '',
        'remaining_amount': '',
        'discount_percentage': '',
        'discount_amount': '',
        'bonus_sessions': '',
        'selected_customer': '',
        'selected_class_type': '',
        'selected_instructor': '',
        'selected_branch': '',
        'selected_class_price': '',
        'payment_type': 'full',
        'payment_method': '',
        'status': '',
        'payment_date': '',
        'amount': '',
        'final_amount': '',
    }
    
    return render(request, 'payments/payment_form.html', context)

@login_required
def payment_edit(request, pk):
    """Chỉnh sửa đơn hàng"""
    payment = get_object_or_404(Payment, pk=pk)
    customers = Customer.objects.all().order_by('full_name')
    class_types = ClassType.objects.all().order_by('name')
    instructors = Instructor.objects.filter(active=True).order_by('full_name')
    branches = Branch.objects.filter(active=True).order_by('name')
    
    # Lấy thông tin về gói tập liên quan để hiển thị
    customer_package = CustomerPackage.objects.filter(payment=payment).first()
    
    if request.method == 'POST':
        # Xử lý form sửa đơn hàng
        customer_id = request.POST.get('customer')
        class_type_id = request.POST.get('class_type')
        class_price_id = request.POST.get('class_price')
        amount = request.POST.get('amount')
        
        # Xử lý ưu đãi
        discount_type = request.POST.get('discount_type')
        discount_percentage = request.POST.get('discount_percentage', '0')
        discount_amount_value = request.POST.get('discount_amount', '0')
        bonus_sessions = request.POST.get('bonus_sessions', '0')
        
        # Xử lý thanh toán một phần
        payment_type = request.POST.get('payment_type', 'full')
        paid_amount = request.POST.get('paid_amount', '0')
        paid_amount_value = request.POST.get('paid_amount_value', '0')
        remaining_payment_due_date = request.POST.get('remaining_payment_due_date')
        
        payment_method = request.POST.get('payment_method')
        payment_date = request.POST.get('payment_date')
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        # Xử lý file chứng từ thanh toán
        payment_proof = request.FILES.get('payment_proof')
        
        # Xử lý instructor
        instructor_id = request.POST.get('instructor')
        instructor = None
        if instructor_id:
            instructor = Instructor.objects.get(id=instructor_id)
        
        # Lấy branch_id
        branch_id = request.POST.get('branch')
        branch = None
        if branch_id:
            branch = Branch.objects.get(id=branch_id)
        
        # Log chi tiết các giá trị nhận được từ form
        print(f"[DEBUG-POST] paid_amount={paid_amount}, paid_amount_value={paid_amount_value}, payment_type={payment_type}, amount={amount}")
        
        try:
            customer = Customer.objects.get(id=customer_id)
            class_type = ClassType.objects.get(id=class_type_id)
            
            # Cập nhật đơn hàng - QUAN TRỌNG: cập nhật giá gốc, không phải giá đã giảm
            # Lấy thông tin giá từ class_price
            # Xử lý chuỗi số tiền: loại bỏ dấu chấm phân cách và đơn vị tiền tệ "VNĐ"
            amount_clean = amount.replace('.', '').replace(' VNĐ', '')
            original_amount = float(amount_clean)
            
            payment.customer = customer
            payment.amount = original_amount  # Đặt lại giá gốc, không phải giá đã giảm
            payment.payment_method = payment_method
            payment.payment_date = payment_date
            payment.status = status
            payment.notes = notes
            payment.class_type = class_type
            payment.payment_type = payment_type
            payment.instructor = instructor
            payment.branch = branch
            
            # Lưu thông tin ưu đãi
            if discount_type == 'percentage':
                payment.discount_type = 'percentage'
                discount_percentage_clean = discount_percentage.replace('.', '').replace(' %', '').replace('%', '')
                payment.discount_value = float(discount_percentage_clean)
            elif discount_type == 'amount':
                payment.discount_type = 'amount'
                discount_amount_clean = discount_amount_value.replace('.', '').replace(' VNĐ', '')
                payment.discount_value = float(discount_amount_clean)
            else:
                payment.discount_type = 'none'
                payment.discount_value = 0
            
            # Xử lý thanh toán một phần
            if payment_type == 'partial':
                # Tính toán giá sau khi giảm giá
                final_amount = payment.final_amount
                
                if paid_amount:
                    # Xử lý chuỗi số tiền: loại bỏ dấu chấm phân cách và đơn vị tiền tệ "VNĐ"
                    paid_amount_clean = paid_amount.replace('.', '').replace(' VNĐ', '')
                    payment.paid_amount = float(paid_amount_clean)
                    payment.remaining_amount = final_amount - float(paid_amount_clean)
                
                if remaining_payment_due_date:
                    payment.remaining_payment_due_date = remaining_payment_due_date
            else:
                # Thanh toán toàn bộ
                payment.paid_amount = payment.final_amount
                payment.remaining_amount = 0
                payment.remaining_payment_due_date = None
            
            # Lưu file chứng từ thanh toán nếu có
            if payment_proof:
                # Tạo thư mục lưu trữ theo ngày tháng nếu chưa có
                upload_dir = f'payment_proofs/{timezone.now().strftime("%Y/%m/%d")}'
                if not os.path.exists(f'media/{upload_dir}'):
                    os.makedirs(f'media/{upload_dir}', exist_ok=True)
                
                # Đổi tên file để tránh trùng lặp
                filename = f"{customer.id}_{timezone.now().strftime('%H%M%S')}_{payment_proof.name}"
                file_path = f'{upload_dir}/{filename}'
                
                with open(f'media/{file_path}', 'wb+') as destination:
                    for chunk in payment_proof.chunks():
                        destination.write(chunk)
                
                # Xóa file cũ nếu có
                if payment.payment_proof:
                    old_file_path = f'media/{payment.payment_proof}'
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                payment.payment_proof = file_path
            
            payment.save()
            
            # Cập nhật gói tập nếu có
            if customer_package:
                class_price = ClassTypePrice.objects.get(id=class_price_id)
                regular_sessions = class_price.number_of_sessions
                total_sessions = regular_sessions + int(bonus_sessions)
                
                # Tính lại số buổi còn lại
                used_sessions = customer_package.total_sessions - customer_package.remaining_sessions
                new_remaining = total_sessions - used_sessions
                
                customer_package.class_type = class_type
                customer_package.total_sessions = total_sessions
                customer_package.remaining_sessions = max(0, new_remaining)
                customer_package.save()
            
            messages.success(request, f'Đã cập nhật đơn hàng cho khách hàng {customer.full_name}')
            return redirect('payment_detail', pk=payment.id)
            
        except (Customer.DoesNotExist, ClassType.DoesNotExist) as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    # Trường hợp GET request, hiển thị form với dữ liệu hiện tại
    context = {
        'customers': customers,
        'class_types': class_types,
        'today_date': timezone.now(),
        'payment_types': Payment.PAYMENT_TYPE_CHOICES,
        'instructors': instructors,
        'payment': payment,
        'customer_package': customer_package,
        'selected_customer': payment.customer.id if payment.customer else None,
        'selected_class_type': payment.class_type.id if payment.class_type else None,
        'selected_instructor': payment.instructor.id if payment.instructor else None,
        'selected_branch': payment.branch.id if payment.branch else None,
        'branches': branches,
    }
    
    # Lấy thông tin về class_price (gói tập) đã chọn
    selected_class_price = None
    default_sessions = 0
    if customer_package and customer_package.class_type:
        # Tìm ClassTypePrice phù hợp dựa trên số buổi và loại lớp
        class_prices = customer_package.class_type.prices.all()
        if class_prices.exists():
            # Tìm gói tập phù hợp nhất với số buổi, ưu tiên số buổi gần nhất
            selected_class_price = min(
                class_prices,
                key=lambda x: abs(x.number_of_sessions - (customer_package.total_sessions - context.get('bonus_sessions', 0)))
            )
            default_sessions = selected_class_price.number_of_sessions
    
    # Tính số buổi bonus
    bonus_sessions = 0
    if customer_package and selected_class_price:
        bonus_sessions = customer_package.total_sessions - selected_class_price.number_of_sessions
    
    # Bổ sung log debug giá trị remaining_amount
    print(f"[DEBUG] payment.id={payment.id}, paid_amount={payment.paid_amount}, remaining_amount={payment.remaining_amount}, final_amount={payment.final_amount}")
    context.update({
        'selected_class_price': selected_class_price.id if selected_class_price else None,
        'bonus_sessions': max(0, bonus_sessions),
        'discount_type': payment.discount_type,
        'discount_percentage': payment.discount_value if payment.discount_type == 'percentage' else '',
        'discount_amount': payment.discount_value if payment.discount_type == 'amount' else '',
        'payment_type': payment.payment_type,
        'payment_method': payment.payment_method,
        'status': payment.status,
        'payment_date': payment.payment_date,
        'paid_amount': payment.paid_amount,
        'remaining_amount': payment.remaining_amount,
        'remaining_payment_due_date': payment.remaining_payment_due_date,
        'amount': payment.amount,
        'final_amount': payment.final_amount,
        'debug_remaining_amount': payment.remaining_amount,
    })
    
    # Xử lý thông tin ưu đãi hiện tại
    if payment.discount_type == 'percentage':
        context['discount_type'] = 'percentage'
        context['discount_percentage'] = payment.discount_value
    elif payment.discount_type == 'amount':
        context['discount_type'] = 'amount'
        context['discount_amount'] = payment.discount_value
    
    return render(request, 'payments/payment_form.html', context)

@login_required
def payment_export_csv(request):
    """Xuất danh sách đơn hàng ra CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=payments-{timezone.now().strftime("%Y%m%d")}.csv'
    
    writer = csv.writer(response)
    writer.writerow([
        'Số hóa đơn', 'Khách hàng', 'Loại lớp', 'Tổng tiền', 
        'Khuyến mãi', 'Thanh toán', 'Ngày', 'Phương thức', 'Trạng thái'
    ])
    
    # Lọc dữ liệu nếu cần
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    
    payments = Payment.objects.select_related('customer', 'class_type')
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__lte=date_to)
        except ValueError:
            pass
    
    if status:
        payments = payments.filter(status=status)
    
    for payment in payments:
        discount_info = ""
        if payment.discount_type and payment.discount_value:
            if payment.discount_type == 'percent':
                discount_info = f"{payment.discount_value}% + {payment.bonus_sessions} buổi"
            else:
                discount_info = f"{payment.discount_value} đ + {payment.bonus_sessions} buổi"
        
        payment_date_display = ""
        if payment.payment_date:
            # Kiểm tra nếu payment_date là datetime object
            if hasattr(payment.payment_date, 'hour'):
                payment_date_display = payment.payment_date.strftime('%d/%m/%Y %H:%M')
            else:
                payment_date_display = payment.payment_date.strftime('%d/%m/%Y')

        writer.writerow([
            payment.invoice_number,
            payment.customer.full_name,
            payment.class_type.name if payment.class_type else '',
            payment.amount,
            discount_info,
            payment.final_amount,
            payment_date_display,
            dict(Payment.PAYMENT_METHOD_CHOICES).get(payment.payment_method, ''),
            dict(Payment.STATUS_CHOICES).get(payment.status, '')
        ])
    
    return response

def package_info_api(request, package_id):
    """API endpoint để lấy thông tin gói tập"""
    try:
        # Log thông tin request
        print(f"Received request for package ID: {package_id}")
        
        # Kiểm tra package_id
        if not package_id or not str(package_id).isdigit():
            return JsonResponse({'error': 'ID gói tập không hợp lệ'}, status=400)
            
        # Lấy thông tin từ class_price thay vì package
        try:
            class_price = ClassTypePrice.objects.get(id=package_id)
        except ClassTypePrice.DoesNotExist:
            return JsonResponse({'error': f'Không tìm thấy gói tập với ID: {package_id}'}, status=404)
        
        print(f"Found class_price: {class_price}")
        
        # Kiểm tra dữ liệu của class_price
        if not hasattr(class_price, 'unit_price') or not hasattr(class_price, 'number_of_sessions'):
            return JsonResponse({'error': 'Dữ liệu gói tập không đầy đủ'}, status=500)
            
        # Kiểm tra class_type
        if not class_price.class_type:
            return JsonResponse({'error': 'Gói tập không có thông tin loại lớp'}, status=500)
        
        # Chuẩn bị dữ liệu trả về
        data = {
            'id': class_price.id,
            'name': f"{class_price.class_type.name} - {class_price.get_class_format_display()} - {class_price.number_of_sessions} buổi",
            'price': float(class_price.unit_price),
            'total_sessions': class_price.number_of_sessions,
            'class_type': class_price.class_type.id,
            'class_type_name': class_price.class_type.name,
        }
        print(f"Returning data: {data}")
        return JsonResponse(data)
    except ClassTypePrice.DoesNotExist:
        print(f"ClassTypePrice with ID {package_id} not found")
        return JsonResponse({'error': 'Gói tập không tồn tại'}, status=404)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in package_info_api: {str(e)}")
        print(f"Error details: {error_details}")
        return JsonResponse({'error': f'Lỗi xử lý: {str(e)}'}, status=500)

def search_customers(request):
    """API endpoint tìm kiếm khách hàng cho select2"""
    search_term = request.GET.get('q', '')
    if not search_term:
        return JsonResponse({"results": []})
    
    customers = Customer.objects.filter(
        full_name__icontains=search_term
    )[:20]  # Giới hạn kết quả để tránh quá tải
    
    results = []
    for customer in customers:
        results.append({
            'id': customer.id,
            'text': customer.full_name,
            'phone': customer.phone,
            'extra_info': f"SĐT: {customer.phone}" if customer.phone else ""
        })
    
    return JsonResponse({
        "results": results
    })

def class_prices_by_type(request, class_type_id):
    """API endpoint để lấy danh sách gói tập theo loại lớp"""
    try:
        class_prices = ClassTypePrice.objects.filter(class_type_id=class_type_id)
        data = []
        
        for price in class_prices:
            data.append({
                'id': price.id,
                'name': f"{price.get_class_format_display()} - {price.number_of_sessions} buổi",
                'price': float(price.unit_price),
                'total_sessions': price.number_of_sessions,
                'time_slot': price.time_slot,
                'time_slot_display': price.get_time_slot_display(),
                'class_format': price.class_format,
                'class_format_display': price.get_class_format_display()
            })
        
        return JsonResponse({"results": data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, id=pk)
    customer_name = payment.customer.full_name
    payment.delete()
    messages.success(request, f'Đã xóa đơn hàng của khách hàng {customer_name}')
    return redirect('payment_list')
