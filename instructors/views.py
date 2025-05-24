from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Instructor
from django.urls import reverse
from decimal import Decimal, InvalidOperation
import traceback
from django.core.exceptions import ValidationError

# Create your views here.

def them_moi(request):
    context = {}
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            full_name=request.POST.get('full_name')
            phone=request.POST.get('phone')
            address=request.POST.get('address')
            
            date_of_birth_str = request.POST.get('date_of_birth')
            date_of_birth = date_of_birth_str if date_of_birth_str else None
            
            gender=request.POST.get('gender')
            bio=request.POST.get('bio')
            certifications=request.POST.get('certifications')
            specialties=request.POST.get('specialties')
            
            hire_date=request.POST.get('hire_date') # Sẽ được validate bởi model nếu blank=False

            # Xử lý đúng cho checkbox 'active'
            active = 'active' in request.POST

            instructor = Instructor(
                full_name=full_name,
                phone=phone,
                address=address,
                date_of_birth=date_of_birth,
                gender=gender,
                bio=bio,
                certifications=certifications,
                specialties=specialties,
                hire_date=hire_date,
                active=active
            )
            
            # Xử lý file ảnh nếu có
            if 'profile_image' in request.FILES:
                instructor.profile_image = request.FILES['profile_image']
            
            # Gọi full_clean để kích hoạt validation của model
            instructor.full_clean()
            # Lưu dữ liệu
            instructor.save()
            
            # Thông báo thành công
            messages.success(request, 'Thêm huấn luyện viên thành công!')
            
            # Redirect về trang danh sách (vẫn comment dòng này để debug)
            # return redirect('instructors:danh_sach') 
            
        except ValidationError as ve:
            error_messages = []
            if hasattr(ve, 'message_dict'):
                for field, field_errors in ve.message_dict.items():
                    field_name = field
                    try:
                        field_name = Instructor._meta.get_field(field).verbose_name
                    except Exception:
                        if field == '__all__':
                            field_name = "Lỗi chung"
                    error_messages.append(f"{field_name}: {'; '.join(field_errors)}")
                    # Đưa lỗi vào context để hiển thị lại trên form
                    context[f'{field}_error'] = '; '.join(field_errors)
                messages.error(request, f"Lỗi xác thực: {'. '.join(error_messages)}")
            else:
                messages.error(request, f"Lỗi xác thực: {'; '.join(ve.messages)}")
            # Giữ lại giá trị đã nhập
            context.update(request.POST.dict())
        except (ValueError, InvalidOperation) as conversion_error:
            messages.error(request, f'Lỗi dữ liệu đầu vào: {str(conversion_error)}')
            context.update(request.POST.dict())
        except Exception as e:
            # Xử lý lỗi và hiển thị thông báo
            messages.error(request, f'Lỗi khi thêm huấn luyện viên: Một lỗi không mong muốn đã xảy ra.')
            context.update(request.POST.dict())
    return render(request, 'instructors/them_moi.html', context)
