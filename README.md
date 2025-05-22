# Pilates CRM - Hệ thống quản lý phòng tập Pilates

Đây là hệ thống quản lý phòng tập Pilates được phát triển bằng Django, cung cấp một CRM đầy đủ chức năng để quản lý khách hàng, lớp học, huấn luyện viên và thanh toán.

## Tính năng

- **Quản lý khách hàng**: Lưu trữ thông tin chi tiết về khách hàng, bao gồm thông tin cá nhân, sức khỏe và lịch sử tham gia.
- **Quản lý lớp học**: Tạo và quản lý các loại lớp học, lịch học, và điểm danh học viên.
- **Quản lý huấn luyện viên**: Theo dõi thông tin huấn luyện viên, lịch dạy, và chuyên môn.
- **Quản lý thành viên**: Theo dõi các gói thành viên, ngày hết hạn, và số buổi tập còn lại.
- **Quản lý thanh toán**: Theo dõi tất cả các khoản thanh toán và chi phí của phòng tập.
- **Giao diện admin thân thiện**: Sử dụng Jazzmin để cung cấp giao diện admin đẹp và dễ sử dụng.

## Cài đặt

1. Clone repository:
```
git clone https://github.com/yourname/pilates-crm.git
cd pilates-crm
```

2. Tạo và kích hoạt môi trường ảo:
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các dependency:
```
pip install -r requirements.txt
```

4. Thực hiện các migration:
```
python manage.py migrate
```

5. Tạo tài khoản superuser:
```
python manage.py createsuperuser
```

6. Khởi động server:
```
python manage.py runserver
```

7. Truy cập trang admin tại http://127.0.0.1:8000/admin/

## Hướng dẫn sử dụng

### Quản lý khách hàng
- Thêm khách hàng mới với đầy đủ thông tin cá nhân, sức khỏe
- Theo dõi lịch sử tham gia các lớp học của khách hàng
- Quản lý thành viên và các gói tập

### Quản lý lớp học
- Tạo các loại lớp học với mức độ khó khác nhau
- Lên lịch học hàng tuần và quản lý phòng học
- Theo dõi điểm danh và tình trạng lớp học

### Quản lý huấn luyện viên
- Quản lý thông tin cá nhân, chứng chỉ và chuyên môn của huấn luyện viên
- Theo dõi lịch dạy và đánh giá

### Quản lý thanh toán
- Ghi nhận các khoản thanh toán từ khách hàng
- Quản lý chi phí của phòng tập
- Tạo báo cáo thu chi

## Yêu cầu hệ thống

- Python 3.8+
- Django 4.2+
- Các package khác được liệt kê trong requirements.txt

## Liên hệ hỗ trợ

Nếu bạn có bất kỳ câu hỏi hoặc cần hỗ trợ, vui lòng liên hệ:
- Email: support@pilates-crm.vn
- Điện thoại: 0123-456-789 