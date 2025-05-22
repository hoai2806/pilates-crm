/**
 * Modern Timepicker - A sleek, modern time picker for Django Admin
 * Phiên bản vanilla JavaScript (không sử dụng jQuery)
 */
document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Khởi tạo timepicker trên các trường thời gian
    function initModernTimepicker() {
        // Lấy tất cả các input time
        const timeInputs = document.querySelectorAll('.field-start_time input[type="text"], .field-end_time input[type="text"]');
        
        // Nếu không có input nào, thoát
        if (timeInputs.length === 0) return;
        
        // Tạo timepicker cho mỗi input
        timeInputs.forEach(function(input) {
            const fieldName = input.getAttribute('name');
            const originalId = input.getAttribute('id');
            
            // Ẩn input gốc
            input.classList.add('hidden-original-time');
            input.style.display = 'none';
            
            // Tạo container chứa timepicker
            const container = document.createElement('div');
            container.className = 'modern-timepicker-container';
            
            // Tạo các thành phần của timepicker
            const hourInput = document.createElement('input');
            hourInput.type = 'text';
            hourInput.className = 'modern-timepicker-hour';
            hourInput.id = originalId + '_hour';
            
            const separator = document.createElement('div');
            separator.className = 'modern-timepicker-separator';
            separator.textContent = ':';
            
            const minuteInput = document.createElement('input');
            minuteInput.type = 'text';
            minuteInput.className = 'modern-timepicker-minute';
            minuteInput.id = originalId + '_minute';
            
            // Thêm các thành phần vào container
            container.appendChild(hourInput);
            container.appendChild(separator);
            container.appendChild(minuteInput);
            
            // Chèn container sau input gốc
            input.parentNode.insertBefore(container, input.nextSibling);
            
            // Tạo container cho slider và các giá trị
            const hourSliderContainer = document.createElement('div');
            hourSliderContainer.className = 'time-slider-container hour-slider';
            
            const minuteSliderContainer = document.createElement('div');
            minuteSliderContainer.className = 'time-slider-container minute-slider';
            
            // Tạo grid cho các giá trị giờ
            const hourValues = document.createElement('div');
            hourValues.className = 'time-values';
            
            for (let i = 0; i < 24; i++) {
                const display = i < 10 ? '0' + i : i;
                const hourValue = document.createElement('div');
                hourValue.className = 'time-value';
                hourValue.setAttribute('data-value', i);
                hourValue.textContent = display;
                hourValues.appendChild(hourValue);
            }
            
            // Tạo grid cho các giá trị phút
            const minuteValues = document.createElement('div');
            minuteValues.className = 'time-values';
            
            for (let i = 0; i < 60; i += 5) {
                const display = i < 10 ? '0' + i : i;
                const minuteValue = document.createElement('div');
                minuteValue.className = 'time-value';
                minuteValue.setAttribute('data-value', i);
                minuteValue.textContent = display;
                minuteValues.appendChild(minuteValue);
            }
            
            // Thêm các giá trị vào các container
            hourSliderContainer.appendChild(hourValues);
            minuteSliderContainer.appendChild(minuteValues);
            
            // Thêm slider containers vào document body
            document.body.appendChild(hourSliderContainer);
            document.body.appendChild(minuteSliderContainer);
            
            // Hàm cập nhật giá trị cho input gốc
            function updateOriginalInput() {
                const hour = hourInput.value || '00';
                const minute = minuteInput.value || '00';
                
                // Cập nhật giá trị cho input gốc với định dạng HH:MM
                input.value = `${hour}:${minute}`;
                
                // Kích hoạt sự kiện change để Django nhận biết sự thay đổi
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
            
            // Xử lý sự kiện khi click vào input hour
            hourInput.addEventListener('focus', function() {
                // Đóng tất cả các slider đang mở
                document.querySelectorAll('.time-slider-container').forEach(function(el) {
                    el.classList.remove('active');
                });
                
                // Lấy vị trí của input
                const rect = hourInput.getBoundingClientRect();
                
                // Thiết lập vị trí cho slider
                hourSliderContainer.style.top = (rect.bottom + window.scrollY) + 'px';
                hourSliderContainer.style.left = (rect.left + window.scrollX) + 'px';
                hourSliderContainer.style.width = rect.width + 'px';
                
                // Hiển thị slider
                hourSliderContainer.classList.add('active');
            });
            
            // Xử lý sự kiện khi click vào input minute
            minuteInput.addEventListener('focus', function() {
                // Đóng tất cả các slider đang mở
                document.querySelectorAll('.time-slider-container').forEach(function(el) {
                    el.classList.remove('active');
                });
                
                // Lấy vị trí của input
                const rect = minuteInput.getBoundingClientRect();
                
                // Thiết lập vị trí cho slider
                minuteSliderContainer.style.top = (rect.bottom + window.scrollY) + 'px';
                minuteSliderContainer.style.left = (rect.left + window.scrollX) + 'px';
                minuteSliderContainer.style.width = rect.width + 'px';
                
                // Hiển thị slider
                minuteSliderContainer.classList.add('active');
            });
            
            // Xử lý sự kiện khi click vào giá trị giờ
            hourValues.addEventListener('click', function(e) {
                if (e.target.classList.contains('time-value')) {
                    const value = parseInt(e.target.getAttribute('data-value'), 10);
                    const display = value < 10 ? '0' + value : value;
                    
                    // Cập nhật giá trị cho input hour
                    hourInput.value = display;
                    
                    // Ẩn slider
                    hourSliderContainer.classList.remove('active');
                    
                    // Cập nhật giá trị cho input gốc
                    updateOriginalInput();
                    
                    // Focus vào input minute
                    minuteInput.focus();
                }
            });
            
            // Xử lý sự kiện khi click vào giá trị phút
            minuteValues.addEventListener('click', function(e) {
                if (e.target.classList.contains('time-value')) {
                    const value = parseInt(e.target.getAttribute('data-value'), 10);
                    const display = value < 10 ? '0' + value : value;
                    
                    // Cập nhật giá trị cho input minute
                    minuteInput.value = display;
                    
                    // Ẩn slider
                    minuteSliderContainer.classList.remove('active');
                    
                    // Cập nhật giá trị cho input gốc
                    updateOriginalInput();
                }
            });
            
            // Đóng tất cả các slider khi click ra ngoài
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.modern-timepicker-container') && 
                    !e.target.closest('.time-slider-container')) {
                    document.querySelectorAll('.time-slider-container').forEach(function(el) {
                        el.classList.remove('active');
                    });
                }
            });
            
            // Xử lý giá trị ban đầu nếu có
            const initialValue = input.value;
            if (initialValue) {
                const timeParts = initialValue.split(':');
                if (timeParts.length >= 2) {
                    hourInput.value = timeParts[0];
                    minuteInput.value = timeParts[1];
                }
            }
            
            // Xử lý khi nhập trực tiếp vào các ô giờ và phút
            hourInput.addEventListener('input', function() {
                let value = this.value;
                
                // Chỉ cho phép nhập số
                value = value.replace(/\D/g, '');
                
                // Giới hạn giá trị từ 0-23
                if (value !== '') {
                    value = Math.min(Math.max(parseInt(value, 10), 0), 23).toString();
                }
                
                // Cập nhật giá trị
                this.value = value;
                
                // Cập nhật input gốc
                updateOriginalInput();
            });
            
            minuteInput.addEventListener('input', function() {
                let value = this.value;
                
                // Chỉ cho phép nhập số
                value = value.replace(/\D/g, '');
                
                // Giới hạn giá trị từ 0-59
                if (value !== '') {
                    value = Math.min(Math.max(parseInt(value, 10), 0), 59).toString();
                }
                
                // Cập nhật giá trị
                this.value = value;
                
                // Cập nhật input gốc
                updateOriginalInput();
            });
        });
    }
    
    // Khởi tạo khi trang đã load xong
    initModernTimepicker();
}); 