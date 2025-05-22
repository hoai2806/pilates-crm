from django.db import migrations

def populate_full_name(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    for customer in Customer.objects.all():
        customer.full_name = f"{customer.last_name} {customer.first_name}"
        customer.save()

class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_alter_customer_options_remove_customer_email_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_full_name),
    ] 