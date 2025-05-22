/**
 * Class Schedule Admin JavaScript
 * Xử lý logic cho form tạo/sửa lịch học
 */
(function($) {
    'use strict';
    
    // Khởi tạo các chức năng cho lịch cố định
    function initRecurringSchedule() {
        const classTypeField = $('#id_class_type');
        const isRecurringField = $('#id_is_recurring');
        const recurringDaysField = $('#id_recurring_days');
        const startDateField = $('#id_start_date');
        const endDateField = $('#id_end_date');
        const dayOfWeekField = $('#id_day_of_week');
        
        // Tạo UI để chọn các ngày trong tuần
        function createDaySelector() {
            const dayNames = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'];
            const container = $('<div class="recurring-days-selector"></div>');
            
            // Thêm label
            container.append('<div class="field-label">Chọn các ngày lặp lại:</div>');
            
            // Tạo checkboxes cho từng ngày trong tuần
            const checkboxContainer = $('<div class="day-checkbox-container"></div>');
            
            for (let i = 0; i < 7; i++) {
                const checkbox = $(`
                    <div class="day-checkbox">
                        <input type="checkbox" id="day-${i}" value="${i}" />
                        <label for="day-${i}">${dayNames[i]}</label>
                    </div>
                `);
                checkboxContainer.append(checkbox);
            }
            
            container.append(checkboxContainer);
            
            // Thêm vào DOM và ẩn ban đầu
            recurringDaysField.closest('.field-recurring_days').append(container);
            recurringDaysField.closest('.field-recurring_days').hide();
            
            // Xử lý khi chọn/bỏ chọn các ngày
            checkboxContainer.on('change', 'input[type="checkbox"]', function() {
                updateRecurringDays();
            });
            
            // Cập nhật giá trị cho trường recurring_days
            function updateRecurringDays() {
                const selectedDays = [];
                
                checkboxContainer.find('input[type="checkbox"]:checked').each(function() {
                    selectedDays.push(parseInt($(this).val(), 10));
                });
                
                // Lưu giá trị vào trường ẩn
                recurringDaysField.val(JSON.stringify(selectedDays));
            }
            
            // Khởi tạo giá trị cho recurring days nếu đã có sẵn
            function initRecurringDays() {
                let selectedDays = [];
                try {
                    const daysValue = recurringDaysField.val();
                    if (daysValue && daysValue !== '') {
                        selectedDays = JSON.parse(daysValue);
                    }
                } catch (e) {
                    console.error('Error parsing recurring days:', e);
                }
                
                // Reset tất cả checkboxes
                checkboxContainer.find('input[type="checkbox"]').prop('checked', false);
                
                // Chọn các ngày đã lưu
                if (Array.isArray(selectedDays)) {
                    selectedDays.forEach(day => {
                        checkboxContainer.find(`input[value="${day}"]`).prop('checked', true);
                    });
                } else if (typeof selectedDays === 'number') {
                    // Trường hợp chỉ có một ngày
                    checkboxContainer.find(`input[value="${selectedDays}"]`).prop('checked', true);
                }
                
                // Nếu chưa có ngày nào được chọn, chọn ngày của day_of_week
                if (checkboxContainer.find('input[type="checkbox"]:checked').length === 0) {
                    const currentDay = dayOfWeekField.val();
                    if (currentDay !== '') {
                        checkboxContainer.find(`input[value="${currentDay}"]`).prop('checked', true);
                        updateRecurringDays();
                    }
                }
            }
            
            // Khởi tạo giá trị ban đầu
            initRecurringDays();
            
            // Khi ngày của week thay đổi, cập nhật lựa chọn ngày lặp lại
            dayOfWeekField.on('change', function() {
                const currentDay = $(this).val();
                
                // Nếu chưa có ngày nào được chọn, chọn ngày hiện tại
                if (checkboxContainer.find('input[type="checkbox"]:checked').length === 0) {
                    checkboxContainer.find(`input[value="${currentDay}"]`).prop('checked', true);
                    updateRecurringDays();
                }
            });
            
            return {
                container,
                update: updateRecurringDays,
                init: initRecurringDays
            };
        }
        
        // Tạo selector cho các ngày lặp lại
        const daySelector = createDaySelector();
        
        // Xử lý hiển thị/ẩn các trường cho lịch lặp lại
        function toggleRecurringFields() {
            const isRecurring = isRecurringField.is(':checked');
            const recurringContainer = $('.field-recurring_days, .field-start_date, .field-end_date');
            
            if (isRecurring) {
                recurringContainer.show();
                daySelector.container.show();
            } else {
                recurringContainer.hide();
                daySelector.container.hide();
            }
        }
        
        // Xử lý hiển thị các trường dựa trên loại lớp
        function toggleByClassType() {
            const classTypeId = classTypeField.val();
            
            if (!classTypeId) return;
            
            // Gửi AJAX request để lấy thông tin loại lớp
            $.ajax({
                url: `/classes/api/class-type/${classTypeId}/`,
                method: 'GET',
                success: function(data) {
                    if (data.class_category === 'fixed') {
                        // Nếu là lớp cố định, bật tính năng lặp lại và hiển thị các trường liên quan
                        isRecurringField.prop('checked', true);
                        isRecurringField.closest('.field-is_recurring').show();
                        toggleRecurringFields();
                    } else {
                        // Nếu không phải lớp cố định, ẩn tính năng lặp lại
                        isRecurringField.closest('.field-is_recurring').hide();
                        $('.field-recurring_days, .field-start_date, .field-end_date').hide();
                        daySelector.container.hide();
                    }
                },
                error: function() {
                    console.error('Failed to fetch class type details');
                }
            });
        }
        
        // Xử lý sự kiện khi form đã load xong
        setTimeout(function() {
            toggleByClassType();
            toggleRecurringFields();
        }, 500);
        
        // Xử lý sự kiện khi thay đổi loại lớp
        classTypeField.on('change', toggleByClassType);
        
        // Xử lý sự kiện khi thay đổi trạng thái lặp lại
        isRecurringField.on('change', toggleRecurringFields);
    }
    
    // Khởi tạo khi trang đã load xong
    $(document).ready(function() {
        initRecurringSchedule();
    });
    
})(django.jQuery); 