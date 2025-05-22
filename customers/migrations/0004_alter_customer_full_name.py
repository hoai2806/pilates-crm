from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_populate_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='full_name',
            field=models.CharField(max_length=100, verbose_name='Họ và tên'),
        ),
    ] 