from django import forms
from customers.models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'full_name', 'phone', 'address',
            'status', 'source',
            'date_of_birth', 'gender', 'profile_image', 'notes',
            'emergency_contact', 'health_issues',
            'parent', 'parent_name', 'parent_phone', 'active',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'health_issues': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đảm bảo tất cả các trường input đều có class form-control hoặc form-select
        for field_name, field in self.fields.items():
            current_attrs = field.widget.attrs
            current_class = current_attrs.get('class', '')
            if isinstance(field.widget, forms.Select):
                if 'form-select' not in current_class:
                    current_attrs['class'] = f'{current_class} form-select'.strip()
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                 if 'form-control' not in current_class:
                    current_attrs['class'] = f'{current_class} form-control'.strip()
 