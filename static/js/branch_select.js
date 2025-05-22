document.addEventListener('DOMContentLoaded', function() {
    // Tìm tất cả các danh sách chi nhánh
    const branchLists = document.querySelectorAll('.field-branches ul');
    
    branchLists.forEach(function(list) {
        // Thêm các class và xử lý sự kiện cho mỗi mục trong danh sách
        const items = list.querySelectorAll('li');
        
        items.forEach(function(item) {
            const checkbox = item.querySelector('input[type="checkbox"]');
            
            // Thêm class selected cho các mục đã được chọn
            if (checkbox.checked) {
                item.classList.add('selected');
            }
            
            // Thêm sự kiện khi người dùng click vào checkbox
            checkbox.addEventListener('change', function() {
                if (checkbox.checked) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });
            
            // Cho phép click vào toàn bộ item để chọn checkbox
            item.addEventListener('click', function(e) {
                // Tránh xung đột khi người dùng click trực tiếp vào checkbox
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    
                    // Kích hoạt sự kiện change
                    const event = new Event('change');
                    checkbox.dispatchEvent(event);
                }
            });
        });
    });
    
    // Thêm nút "Chọn tất cả" và "Bỏ chọn tất cả"
    branchLists.forEach(function(list) {
        if (list.childElementCount > 0) {
            const container = list.parentElement;
            
            // Tạo div chứa các nút
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'branch-select-buttons';
            buttonContainer.style.marginBottom = '10px';
            
            // Nút "Chọn tất cả"
            const selectAllButton = document.createElement('button');
            selectAllButton.type = 'button';
            selectAllButton.className = 'button';
            selectAllButton.textContent = 'Chọn tất cả';
            selectAllButton.onclick = function() {
                const checkboxes = list.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(function(checkbox) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change'));
                });
                return false;
            };
            
            // Nút "Bỏ chọn tất cả"
            const deselectAllButton = document.createElement('button');
            deselectAllButton.type = 'button';
            deselectAllButton.className = 'button';
            deselectAllButton.style.marginLeft = '10px';
            deselectAllButton.textContent = 'Bỏ chọn tất cả';
            deselectAllButton.onclick = function() {
                const checkboxes = list.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(function(checkbox) {
                    checkbox.checked = false;
                    checkbox.dispatchEvent(new Event('change'));
                });
                return false;
            };
            
            // Thêm các nút vào container
            buttonContainer.appendChild(selectAllButton);
            buttonContainer.appendChild(deselectAllButton);
            
            // Chèn container trước danh sách
            container.insertBefore(buttonContainer, list);
        }
    });
    
    // Định dạng giá tiền
    function formatPriceInput(input) {
        // Loại bỏ tất cả các ký tự không phải số
        let value = input.value.replace(/[^\d]/g, '');
        
        // Định dạng với dấu "." phân tách hàng nghìn
        if (value) {
            value = parseInt(value).toLocaleString('vi-VN');
        }
        
        // Thêm đơn vị tiền tệ
        input.value = value;
    }
    
    // Áp dụng cho tất cả các input có class price-format
    const priceInputs = document.querySelectorAll('.price-format');
    priceInputs.forEach(function(input) {
        // Định dạng ban đầu
        formatPriceInput(input);
        
        // Định dạng khi người dùng nhập liệu
        input.addEventListener('input', function() {
            const cursorPosition = input.selectionStart;
            const valueBeforeFormat = input.value.replace(/[^\d]/g, '');
            formatPriceInput(input);
            
            // Cố gắng giữ vị trí con trỏ
            const valueAfterFormat = input.value.replace(/[^\d]/g, '');
            if (valueBeforeFormat === valueAfterFormat) {
                input.setSelectionRange(cursorPosition, cursorPosition);
            }
        });
        
        // Khi focus, hiển thị chỉ số
        input.addEventListener('focus', function() {
            input.value = input.value.replace(/[^\d]/g, '');
        });
        
        // Khi blur, định dạng lại
        input.addEventListener('blur', function() {
            formatPriceInput(input);
        });
    });
}); 