from django_setup import setup_django
setup_django()

from classes.models import ClassType, ClassTypePrice
from branches.models import Branch

# Tạo hoặc lấy loại lớp
ct, created = ClassType.objects.get_or_create(
    name='Bàn chân bẹt - Nhóm 1:6 - X-Pilates',
    defaults={
        'duration': 60,
        'max_capacity': 12,
        'difficulty_level': 2,
        'class_category': 'registration',
    }
)

# Gán chi nhánh X-Pilates
branch = Branch.objects.filter(name__icontains='X-Pilates').first()
if branch:
    ct.branches.add(branch)

# Xóa bảng giá cũ (nếu có)
ClassTypePrice.objects.filter(class_type=ct, class_format='GROUP_6').delete()

# Nhập bảng giá mới
price_data = [
    ('MORNING_LOW', 1, 250000), ('MORNING_LOW', 10, 220000), ('MORNING_LOW', 20, 200000), ('MORNING_LOW', 60, 180000), ('MORNING_LOW', 90, 160000), ('MORNING_LOW', 120, 140000),
    ('MORNING_MID', 1, 300000), ('MORNING_MID', 10, 270000), ('MORNING_MID', 20, 250000), ('MORNING_MID', 60, 220000), ('MORNING_MID', 90, 190000), ('MORNING_MID', 120, 160000),
    ('MORNING_PEAK', 1, 350000), ('MORNING_PEAK', 10, 300000), ('MORNING_PEAK', 20, 270000), ('MORNING_PEAK', 60, 240000), ('MORNING_PEAK', 90, 220000), ('MORNING_PEAK', 120, 200000),
    ('AFTERNOON_LOW', 1, 250000), ('AFTERNOON_LOW', 10, 220000), ('AFTERNOON_LOW', 20, 200000), ('AFTERNOON_LOW', 60, 180000), ('AFTERNOON_LOW', 90, 160000), ('AFTERNOON_LOW', 120, 140000),
    ('AFTERNOON_MID', 1, 350000), ('AFTERNOON_MID', 10, 300000), ('AFTERNOON_MID', 20, 270000), ('AFTERNOON_MID', 60, 240000), ('AFTERNOON_MID', 90, 220000), ('AFTERNOON_MID', 120, 200000),
    ('AFTERNOON_PEAK', 1, 420000), ('AFTERNOON_PEAK', 10, 360000), ('AFTERNOON_PEAK', 20, 340000), ('AFTERNOON_PEAK', 60, 300000), ('AFTERNOON_PEAK', 90, 270000), ('AFTERNOON_PEAK', 120, 240000),
]
for idx, (time_slot, num_sessions, unit_price) in enumerate(price_data):
    ClassTypePrice.objects.create(
        class_type=ct,
        class_format='GROUP_6',
        time_slot=time_slot,
        number_of_sessions=num_sessions,
        unit_price=unit_price,
        order=idx
    )
print('Đã nhập xong bảng giá lớp nhóm 1:6 bàn chân bẹt cho X-Pilates!') 