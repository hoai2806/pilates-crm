document.addEventListener('DOMContentLoaded', function() {
    // Hàm định dạng số tiền theo kiểu Việt Nam (dấu . phân tách hàng nghìn và vnđ ở cuối)
    function formatVietnameseCurrency(number) {
        return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' vnđ';
    }
    
    // Lấy tất cả các trường nhập liệu đơn giá
    const priceInputs = document.querySelectorAll('.field-unit_price input');
    
    priceInputs.forEach(function(input) {
        // Định dạng ban đầu nếu có giá trị
        if (input.value) {
            const numericValue = parseFloat(input.value.replace(/[^\d]/g, ''));
            if (!isNaN(numericValue)) {
                const displayValue = formatVietnameseCurrency(numericValue);
                input.setAttribute('data-original-value', numericValue);
                input.value = displayValue;
                
                // Tính toán thành tiền ban đầu
                calculateTotalPrice(input);
            }
        }
        
        // Khi focus vào trường nhập liệu, hiển thị giá trị gốc
        input.addEventListener('focus', function() {
            const originalValue = input.getAttribute('data-original-value');
            if (originalValue) {
                input.value = originalValue;
            } else {
                input.value = input.value.replace(/[^\d]/g, '');
            }
        });
        
        // Khi blur (nhấp ra ngoài), định dạng lại giá trị
        input.addEventListener('blur', function() {
            if (input.value) {
                const numericValue = parseFloat(input.value.replace(/[^\d]/g, ''));
                if (!isNaN(numericValue)) {
                    const displayValue = formatVietnameseCurrency(numericValue);
                    input.setAttribute('data-original-value', numericValue);
                    input.value = displayValue;
                    
                    // Tính toán lại thành tiền
                    calculateTotalPrice(input);
                }
            }
        });
        
        // Chỉ cho phép nhập số
        input.addEventListener('input', function(e) {
            const inputValue = input.value;
            const numericValue = inputValue.replace(/[^\d]/g, '');
            
            if (inputValue !== numericValue) {
                input.value = numericValue;
            }
            
            // Tính và cập nhật thành tiền
            calculateTotalPrice(input);
        });
    });
    
    // Định dạng lại tất cả các giá trị đơn giá khi trang được tải
    setTimeout(function() {
        priceInputs.forEach(function(input) {
            if (input.value && !input.value.includes('vnđ')) {
                const numericValue = parseFloat(input.value.replace(/[^\d]/g, ''));
                if (!isNaN(numericValue)) {
                    const displayValue = formatVietnameseCurrency(numericValue);
                    input.setAttribute('data-original-value', numericValue);
                    input.value = displayValue;
                }
            }
        });
    }, 300);
    
    // Hàm tính và cập nhật thành tiền
    function calculateTotalPrice(unitPriceInput) {
        // Tìm row cha
        const row = unitPriceInput.closest('tr');
        if (!row) return;
        
        // Tìm các phần tử liên quan
        const sessionsInput = row.querySelector('.field-number_of_sessions input');
        const totalPriceCell = row.querySelector('.field-get_total_price');
        
        if (!sessionsInput || !totalPriceCell) return;
        
        // Lấy giá trị
        const unitPrice = parseFloat(unitPriceInput.value.replace(/[^\d\-+.,]/g, '').replace(/\./g, '').replace(/,/g, '.')) || 0;
        const sessions = parseInt(sessionsInput.value) || 0;
        
        // Tính tổng
        const totalPrice = unitPrice * sessions;
        
        // Cập nhật hiển thị
        if (totalPrice > 0) {
            const formattedTotal = formatVietnameseCurrency(totalPrice);
            totalPriceCell.innerHTML = '<span style="font-weight: bold; color: #0066cc;">' + formattedTotal + '</span>';
        } else {
            totalPriceCell.innerHTML = '-';
        }
    }
    
    // Đăng ký sự kiện cho các trường nhập số buổi
    const sessionInputs = document.querySelectorAll('.field-number_of_sessions input');
    sessionInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const row = input.closest('tr');
            if (!row) return;
            
            const unitPriceInput = row.querySelector('.field-unit_price input');
            if (unitPriceInput) {
                calculateTotalPrice(unitPriceInput);
            }
        });
        
        // Kích hoạt sự kiện input để tính toán thành tiền ban đầu
        const event = new Event('input', { bubbles: true });
        input.dispatchEvent(event);
    });
    
    // Cập nhật tất cả các thành tiền khi trang được tải
    setTimeout(function() {
        priceInputs.forEach(function(input) {
            calculateTotalPrice(input);
        });
    }, 500);
    
    // Đảm bảo lưu giá trị số thực khi submit form
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Lấy tất cả các trường đơn giá và chuyển về dạng số
            priceInputs.forEach(function(input) {
                if (input.value.includes('vnđ')) {
                    const originalValue = input.getAttribute('data-original-value');
                    if (originalValue) {
                        input.value = originalValue;
                    } else {
                        input.value = input.value.replace(/[^\d]/g, '');
                    }
                }
            });
        });
    });
}); 