from django import forms
from classes.models import ClassSchedule, ClassType
from instructors.models import Instructor
from branches.models import Branch
from django.utils import timezone
from datetime import datetime, time

class ClassScheduleForm(forms.ModelForm):
    # Thêm trường không có trong model nhưng cần thiết cho form
    weekdays = forms.MultipleChoiceField(
        choices=ClassSchedule.DAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Các ngày trong tuần"
    )
    
    schedule_type = forms.ChoiceField(
        choices=[('recurring', 'Lịch lặp lại'), ('specific', 'Buổi học cụ thể')],
        widget=forms.RadioSelect,
        initial='recurring',
        label="Loại lịch"
    )
    
    class Meta:
        model = ClassSchedule
        fields = ['class_type', 'instructor', 'room', 'start_date', 'end_date', 
                 'start_time', 'end_time', 'specific_date', 'is_recurring']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'specific_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        schedule_type = cleaned_data.get('schedule_type')
        
        if schedule_type == 'recurring':
            if not cleaned_data.get('weekdays'):
                self.add_error('weekdays', 'Vui lòng chọn ít nhất một ngày trong tuần')
            # Đảm bảo is_recurring được đặt đúng
            cleaned_data['is_recurring'] = True
        elif schedule_type == 'specific':
            if not cleaned_data.get('specific_date'):
                self.add_error('specific_date', 'Vui lòng chọn ngày cụ thể')
            # Đảm bảo is_recurring được đặt đúng
            cleaned_data['is_recurring'] = False
        
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Xử lý recurring_days từ weekdays
        if self.cleaned_data.get('schedule_type') == 'recurring' and self.cleaned_data.get('weekdays'):
            instance.recurring_days = [int(day) for day in self.cleaned_data.get('weekdays')]
            
            # Đặt day_of_week là ngày đầu tiên trong recurring_days
            if instance.recurring_days:
                instance.day_of_week = instance.recurring_days[0]
        
        if commit:
            instance.save()
        
        return instance 