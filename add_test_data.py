from django.utils import timezone
from datetime import timedelta, time
from classes.models import ClassType, Instructor, ClassSchedule
import random

print("Bắt đầu tạo dữ liệu lịch học mẫu...")

# Xóa tất cả dữ liệu lịch học cũ
print("Đang xóa dữ liệu lịch học cũ...")
ClassSchedule.objects.all().delete()
print("Đã xóa tất cả dữ liệu lịch học cũ")

# Lấy ngày hiện tại
start_date = timezone.now().date()

# Lấy danh sách ID của huấn luyện viên và loại lớp học
instructor_ids = list(Instructor.objects.values_list('id', flat=True))
class_type_ids = list(ClassType.objects.values_list('id', flat=True))

# Tạo lịch học mẫu
count = 0
for class_type_id in class_type_ids:
    class_type = ClassType.objects.get(id=class_type_id)
    print(f"Đang tạo lịch học cho {class_type.name}")
    
    for weekday in range(7):
        for hour in [7, 9, 15, 17, 19]:
            # 30% cơ hội tạo lịch cho mỗi ngày và giờ
            if random.random() < 0.3:
                count += 1
                instructor_id = random.choice(instructor_ids)
                instructor = Instructor.objects.get(id=instructor_id)
                
                # Tạo giờ bắt đầu và kết thúc
                start_time = time(hour, 0)
                end_time = time(hour + 1, 0)
                
                # Tạo lịch học
                room = f'Phòng {random.randint(1, 5)}'
                schedule = ClassSchedule.objects.create(
                    class_type=class_type,
                    instructor=instructor,
                    day_of_week=weekday,
                    start_time=start_time,
                    end_time=end_time,
                    room=room,
                    is_recurring=True,
                    recurring_days=[weekday],
                    start_date=start_date,
                    end_date=start_date + timedelta(days=90)
                )
                print(f"  Đã tạo lịch: {schedule}")

print(f"Đã tạo tổng cộng {count} lịch học tự động")
print("Đang tạo các phiên học (class sessions) từ lịch học...")

# Tạo các phiên học cụ thể từ lịch lặp lại
for schedule in ClassSchedule.objects.filter(is_recurring=True):
    schedule.generate_class_sessions()

print("Đã tạo xong dữ liệu mẫu!") 