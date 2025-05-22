from django.db import migrations

def create_branches(apps, schema_editor):
    Branch = apps.get_model('branches', 'Branch')
    
    # Tạo chi nhánh mẫu nếu chưa có
    if not Branch.objects.exists():
        branch = Branch.objects.create(
            name="Chi nhánh trung tâm",
            address="123 Đường Nguyễn Huệ, Quận 1, TP.HCM",
            phone_number="0987654321",
            description="Chi nhánh chính của HD Pilates Studio",
            active=True,
            has_elevator=True,
            has_wifi=True,
            has_lockers=True,
            has_shower=True,
            has_parking=True,
            has_towel_service=True
        )


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_branches),
    ] 