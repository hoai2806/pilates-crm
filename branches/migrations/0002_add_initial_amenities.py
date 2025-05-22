from django.db import migrations


def create_amenities(apps, schema_editor):
    Amenity = apps.get_model('branches', 'Amenity')
    
    # General amenities
    general_amenities = [
        {'name': 'Thang máy', 'category': 'general', 'icon': 'fas fa-elevator'},
        {'name': 'Wifi', 'category': 'general', 'icon': 'fas fa-wifi'},
        {'name': 'Tủ khóa', 'category': 'general', 'icon': 'fas fa-lock'},
        {'name': 'Phòng tắm', 'category': 'general', 'icon': 'fas fa-shower'},
    ]
    
    for amenity_data in general_amenities:
        Amenity.objects.create(**amenity_data)
    
    # Parking amenities
    parking_amenities = [
        {'name': 'Bãi đỗ xe', 'category': 'parking', 'icon': 'fas fa-parking'},
        {'name': 'Giá để xe đạp', 'category': 'parking', 'icon': 'fas fa-bicycle'},
        {'name': 'Bãi đỗ xe cho người khuyết tật', 'category': 'parking', 'icon': 'fas fa-wheelchair'},
    ]
    
    for amenity_data in parking_amenities:
        Amenity.objects.create(**amenity_data)
    
    # Other amenities
    other_amenities = [
        {'name': 'Dịch vụ khăn tắm', 'category': 'others', 'icon': 'fas fa-tshirt'},
        {'name': 'Đồ ăn/thức uống', 'category': 'others', 'icon': 'fas fa-utensils'},
        {'name': 'Nhà vệ sinh không phân biệt giới tính', 'category': 'others', 'icon': 'fas fa-restroom'},
        {'name': 'Dịch vụ trông trẻ', 'category': 'others', 'icon': 'fas fa-baby'},
    ]
    
    for amenity_data in other_amenities:
        Amenity.objects.create(**amenity_data)


def delete_amenities(apps, schema_editor):
    Amenity = apps.get_model('branches', 'Amenity')
    Amenity.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_amenities, delete_amenities),
    ] 