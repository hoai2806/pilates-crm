(function($) {
    $(document).ready(function() {
        const classTypeField = $('#id_class_type');
        const classPriceField = $('#id_class_price');
        const packageOptionsField = $('<select id="package_options_select" class="select form-control">').insertAfter(classTypeField);
        
        // Ẩn trường class_price gốc
        classPriceField.closest('.form-row').hide();
        
        // Thêm label và wrapper cho trường mới
        packageOptionsField.wrap('<div class="form-row field-package_options"></div>');
        
        $('<div class="field-box">').insertBefore(packageOptionsField).append(
            $('<label for="package_options_select">').text('Gói buổi tập:')
        );
        
        // Thêm các field hiển thị giá
        const unitPriceDisplay = $('<div class="form-row field-unit_price"><div class="field-box"><label>Đơn giá:</label><span id="unit_price_display" style="padding: 10px; display: inline-block; font-weight: bold;">0 VNĐ</span></div></div>').insertAfter(packageOptionsField.closest('.form-row'));
        
        const totalPriceDisplay = $('<div class="form-row field-total_price"><div class="field-box"><label>Thành tiền:</label><span id="total_price_display" style="padding: 10px; display: inline-block; font-weight: bold; color: #d9534f;">0 VNĐ</span></div></div>').insertAfter(unitPriceDisplay);
        
        // Khởi tạo các trường
        packageOptionsField.prop('disabled', true).append(
            $('<option value="">').text('Vui lòng chọn loại lớp học trước')
        );
        
        // Lưu trữ dữ liệu giá của loại lớp hiện tại
        let currentPricesData = [];
        
        function updatePackageOptions() {
            const classTypeId = classTypeField.val();
            
            // Reset các trường phụ thuộc
            packageOptionsField.empty();
            $('#unit_price_display').text('0 VNĐ');
            $('#total_price_display').text('0 VNĐ');
            $('#id_amount').val('');
            $('#id_final_amount').val('');
            
            if (classTypeId) {
                // Kích hoạt và hiển thị "Đang tải..."
                packageOptionsField.prop('disabled', true);
                packageOptionsField.append($('<option>').text('Đang tải...'));
                
                // Tải danh sách gói buổi học dựa trên loại lớp
                fetchClassPrices(classTypeId);
            } else {
                // Nếu không có class_type nào được chọn
                packageOptionsField.empty();
                packageOptionsField.prop('disabled', true);
                packageOptionsField.append($('<option>').text('Vui lòng chọn loại lớp học trước'));
            }
        }
        
        function fetchClassPrices(classTypeId) {
            $.ajax({
                url: '/payments/api/class-prices/' + classTypeId + '/',
                type: 'GET',
                success: function(data) {
                    packageOptionsField.empty();
                    
                    if (data && data.prices && data.prices.length > 0) {
                        // Lưu lại dữ liệu giá
                        currentPricesData = data.prices;
                        
                        // Thêm tùy chọn mặc định
                        packageOptionsField.append(
                            $('<option value="" selected>').text('--- Chọn gói buổi tập ---')
                        );
                        
                        // Thêm tất cả các gói với thông tin đầy đủ
                        data.prices.forEach(price => {
                            const formatDisplay = price.class_format === 'private' ? 'PT (Cá nhân)' : 'Nhóm';
                            const optionText = `${formatDisplay} - ${price.number_of_sessions} buổi`;
                            
                            packageOptionsField.append(
                                $('<option>')
                                    .val(price.id)
                                    .text(optionText)
                                    .data('price', price)
                            );
                        });
                        
                        // Nếu chỉ có một gói, tự động chọn
                        if (data.prices.length === 1) {
                            packageOptionsField.val(data.prices[0].id);
                            packageOptionsField.trigger('change');
                        }
                        
                        // Kích hoạt trường
                        packageOptionsField.prop('disabled', false);
                    } else {
                        // Nếu không có dữ liệu
                        packageOptionsField.append($('<option>').text('Không có gói buổi tập nào cho loại lớp này'));
                        packageOptionsField.prop('disabled', true);
                    }
                },
                error: function(xhr, status, error) {
                    packageOptionsField.empty();
                    packageOptionsField.append($('<option>').text('Lỗi khi tải dữ liệu'));
                    packageOptionsField.prop('disabled', true);
                }
            });
        }
        
        function updatePriceInfo() {
            const priceId = packageOptionsField.val();
            
            if (priceId) {
                // Lấy dữ liệu giá từ option đã chọn
                const selectedOption = packageOptionsField.find('option:selected');
                const priceData = selectedOption.data('price');
                
                if (priceData) {
                    // Cập nhật giá trị classPriceField (trường ẩn)
                    classPriceField.val(priceData.id);
                    
                    // Hiển thị đơn giá
                    const unitPrice = new Intl.NumberFormat('vi-VN').format(priceData.unit_price);
                    $('#unit_price_display').text(`${unitPrice} VNĐ`);
                    
                    // Hiển thị thành tiền
                    const totalPrice = new Intl.NumberFormat('vi-VN').format(priceData.total_price);
                    $('#total_price_display').text(`${totalPrice} VNĐ`);
                    
                    // Cập nhật tổng tiền
                    $('#id_amount').val(priceData.total_price);
                    
                    // Tính lại giá trị final_amount
                    const discountType = $('#id_discount_type').val();
                    const discountValue = parseFloat($('#id_discount_value').val()) || 0;
                    let finalAmount = priceData.total_price;
                    
                    if (discountType === 'percent') {
                        finalAmount = priceData.total_price * (1 - discountValue / 100);
                    } else if (discountType === 'amount') {
                        finalAmount = priceData.total_price - discountValue;
                    }
                    
                    $('#id_final_amount').val(finalAmount);
                }
            } else {
                // Reset giá nếu không có gói nào được chọn
                $('#unit_price_display').text('0 VNĐ');
                $('#total_price_display').text('0 VNĐ');
                $('#id_amount').val('');
                $('#id_final_amount').val('');
                classPriceField.val('');
            }
        }
        
        // Cập nhật khi trang đã tải xong
        updatePackageOptions();
        
        // Đăng ký sự kiện thay đổi
        classTypeField.on('change', updatePackageOptions);
        packageOptionsField.on('change', updatePriceInfo);
        
        // Xử lý khi giá trị khuyến mãi thay đổi
        $('#id_discount_type, #id_discount_value').on('change', function() {
            // Tính lại giá trị final_amount dựa trên giá trị amount hiện tại
            const amount = parseFloat($('#id_amount').val()) || 0;
            const discountType = $('#id_discount_type').val();
            const discountValue = parseFloat($('#id_discount_value').val()) || 0;
            let finalAmount = amount;
            
            if (discountType === 'percent') {
                finalAmount = amount * (1 - discountValue / 100);
            } else if (discountType === 'amount') {
                finalAmount = amount - discountValue;
            }
            
            $('#id_final_amount').val(finalAmount);
            
            // Cập nhật hiển thị final_amount
            const finalAmountFormatted = new Intl.NumberFormat('vi-VN').format(finalAmount);
            $('#total_price_display').text(`${finalAmountFormatted} VNĐ`);
        });
    });
})(django.jQuery); 