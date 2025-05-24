(function($) {
    $(document).ready(function() {
        let currentPricesData = [];

        $('#class_type').change(function() {
            const classTypeId = $(this).val();
            if (classTypeId) {
                $.ajax({
                    url: '/payments/api/class-prices/' + classTypeId + '/',
                    type: 'GET',
                    success: function(data) {
                        const $classPrice = $('#class_price');
                        $classPrice.empty();
                        if (data && data.results && data.results.length > 0) {
                            currentPricesData = data.results;
                            $classPrice.append('<option value="">-- Chọn gói tập --</option>');
                            data.results.forEach(price => {
                                let optionText = price.name;
                                if (price.time_slot_display) {
                                    optionText += ' (Khung giờ: ' + price.time_slot_display + ')';
                                }
                                $classPrice.append(
                                    $('<option>')
                                        .val(price.id)
                                        .text(optionText)
                                );
                            });
                        } else {
                            $classPrice.append('<option value="">Không có gói tập nào</option>');
                        }
                    }
                });
            } else {
                $('#class_price').empty().append('<option value="">-- Chọn gói tập --</option>');
                $('#sessions').val('0');
                $('#total_amount').val('');
                $('#unit_price_display').text('');
                $('#total_amount').data('original', 0);
                updateTotals();
            }
        });

        $('#class_price').change(function() {
            const priceId = $(this).val();
            if (!priceId) {
                $('#sessions').val('0');
                $('#total_amount').val('');
                $('#unit_price_display').text('');
                $('#total_amount').data('original', 0);
                updateTotals();
                return;
            }
            const price = currentPricesData.find(p => p.id == priceId);
            if (price) {
                $('#sessions').val(price.total_sessions);
                $('#unit_price_display').text(price.price.toLocaleString('vi-VN'));
                const total = price.price * price.total_sessions;
                $('#total_amount').data('original', total);
                $('#total_amount').val(total.toLocaleString('vi-VN'));
                updateTotals();
            } else {
                $('#sessions').val('0');
                $('#total_amount').val('');
                $('#unit_price_display').text('');
                $('#total_amount').data('original', 0);
                updateTotals();
            }
        });

        $('#bonus_sessions').on('input change', function() {
            const bonus = parseInt($(this).val()) || 0;
            const priceId = $('#class_price').val();
            let baseSessions = 0;
            let unitPrice = 0;
            if (priceId) {
                const price = currentPricesData.find(p => p.id == priceId);
                if (price) {
                    baseSessions = price.total_sessions;
                    unitPrice = price.price;
                }
            }
            const totalSessions = baseSessions + bonus;
            $('#sessions').val(totalSessions);
            const totalAmount = unitPrice * totalSessions;
            $('#total_amount').data('original', totalAmount);
            $('#total_amount').val(totalAmount ? totalAmount.toLocaleString('vi-VN') : '');
            updateTotals();
        });

        function updateTotals() {
            const amount = $('#total_amount').data('original') || 0;
            let discount = 0;
            let final = amount;
            const discountType = $('input[name="discount_type"]:checked').val();
            if (discountType === 'percentage') {
                const percent = parseFloat($('#discount_percentage_value').val()) || 0;
                discount = Math.round(amount * percent / 100);
            } else if (discountType === 'amount') {
                discount = parseInt($('#discount_amount_value').val().replace(/\D/g, '')) || 0;
            }
            final = amount - discount;
            if (final < 0) final = 0;
            $('#original-amount').text(amount.toLocaleString('vi-VN') + ' VNĐ');
            $('#discount-amount').text(discount.toLocaleString('vi-VN') + ' VNĐ');
            $('#final-amount').text(final.toLocaleString('vi-VN') + ' VNĐ');
            
            // Chỉ cập nhật giá trị khi không phải chế độ sửa
            if (!window.isEditMode) {
                $('#total_amount').val(final.toLocaleString('vi-VN'));
                $('#payment_amount').val(final.toLocaleString('vi-VN'));
                $('#payment_amount_value').val(final);
            }
        }

        $('input[name="discount_type"], #discount_percentage_value, #discount_amount_value').on('input change', function() {
            updateTotals();
        });

        function showFullPayment() {
            $('#full_payment_section').show();
            $('#partial_payment_section').hide();
            // Chỉ cập nhật giá trị khi không phải chế độ sửa
            if (!window.isEditMode) {
                const final = getFinalAmount();
                $('#payment_amount').val(final.toLocaleString('vi-VN'));
                $('#payment_amount_value').val(final);
            }
        }
        function showPartialPayment() {
            $('#full_payment_section').hide();
            $('#partial_payment_section').show();
            // Chỉ cập nhật giá trị khi không phải chế độ sửa
            if (!window.isEditMode) {
                $('#paid_amount').val('');
                $('#paid_amount_value').val('');
                const final = getFinalAmount();
                $('#remaining_amount').val(final.toLocaleString('vi-VN'));
                $('#remaining_amount_value').val(final);
            }
        }
        function getFinalAmount() {
            // Lấy số tiền thành tiền hiện tại
            const text = $('#final-amount').text().replace(/\D/g, '');
            return parseInt(text) || 0;
        }
        // Sự kiện chọn hình thức thanh toán
        $('input[name="payment_type"]').change(function() {
            if ($(this).val() === 'partial') {
                showPartialPayment();
            } else {
                showFullPayment();
            }
        });
        // Khi nhập số tiền thanh toán trước
        $('#paid_amount').on('input change', function() {
            let paid = parseInt($(this).val().replace(/\D/g, '')) || 0;
            const final = getFinalAmount();
            if (paid > final) paid = final;
            $(this).val(paid.toLocaleString('vi-VN'));
            $('#paid_amount_value').val(paid);
            
            // Chỉ cập nhật số tiền còn lại khi không phải chế độ sửa
            if (!window.isEditMode) {
                const remain = final - paid;
                $('#remaining_amount').val(remain.toLocaleString('vi-VN'));
                $('#remaining_amount_value').val(remain);
            }
        });
        // Khi thay đổi thành tiền, cập nhật lại các trường liên quan
        function syncPartialPayment() {
            if ($('input[name="payment_type"]:checked').val() === 'partial') {
                const final = getFinalAmount();
                let paid = parseInt($('#paid_amount').val().replace(/\D/g, '')) || 0;
                if (paid > final) paid = final;
                // TẠM THỜI KHÔNG SET LẠI GIÁ TRỊ paid_amount ĐỂ TEST
                // $('#paid_amount').val(paid ? paid.toLocaleString('vi-VN') : '');
                $('#paid_amount_value').val(paid);
                // TẠM THỜI KHÔNG SET LẠI remaining_amount ĐỂ TEST
                // if (window.isEditMode && $('#remaining_amount').data('from-backend')) {
                //     return;
                // }
                // const remain = final - paid;
                // $('#remaining_amount').val(remain.toLocaleString('vi-VN'));
                // $('#remaining_amount_value').val(remain);
            } else {
                showFullPayment();
            }
        }
        // Gọi lại khi thay đổi tổng tiền
        const oldUpdateTotals = updateTotals;
        updateTotals = function() {
            oldUpdateTotals();
            syncPartialPayment();
        }
        // Nếu là chế độ sửa, không gọi updateTotals, showFullPayment, showPartialPayment khi load trang
        if (!window.isEditMode) {
            if ($('input[name="payment_type"]:checked').val() === 'partial') {
                showPartialPayment();
            } else {
                showFullPayment();
            }
            updateTotals();
        }

        if ($('#customer').length && $.fn.select2) {
            $('#customer').select2({
                placeholder: 'Chọn khách hàng',
                allowClear: true,
                width: '100%'
            });
        }

        // --- TỰ ĐỘNG FILL GÓI TẬP KHI SỬA ĐƠN HÀNG ---
        const selectedClassType = $('#class_type').data('selected') || $('#class_type').val();
        const selectedClassPrice = $('#class_price').data('selected') || $('#class_price').val();
        if (selectedClassType && selectedClassPrice) {
            // Gọi API lấy danh sách gói tập theo loại lớp
            $.ajax({
                url: '/payments/api/class-prices/' + selectedClassType + '/',
                type: 'GET',
                success: function(data) {
                    const $classPrice = $('#class_price');
                    $classPrice.empty();
                    if (data && data.results && data.results.length > 0) {
                        currentPricesData = data.results;
                        $classPrice.append('<option value="">-- Chọn gói tập --</option>');
                        data.results.forEach(price => {
                            let optionText = price.name;
                            if (price.time_slot_display) {
                                optionText += ' (Khung giờ: ' + price.time_slot_display + ')';
                            }
                            const selected = (price.id == selectedClassPrice) ? 'selected' : '';
                            $classPrice.append(
                                $('<option>')
                                    .val(price.id)
                                    .text(optionText)
                                    .prop('selected', price.id == selectedClassPrice)
                            );
                        });
                        // Trigger change để fill lại các trường liên quan
                        $classPrice.trigger('change');
                    } else {
                        $classPrice.append('<option value="">Không có gói tập nào</option>');
                    }
                }
            });
        }

        // Hiển thị đúng input ưu đãi khi load trang
        function updateDiscountInputs() {
            var type = $('input[name="discount_type"]:checked').val();
            $('.discount-amount').hide();
            if (type === 'percentage') {
                $('#discount_percentage_value').closest('.discount-amount').show();
            } else if (type === 'amount') {
                $('#discount_amount_value').closest('.discount-amount').show();
            }
        }
        updateDiscountInputs();
        $('input[name="discount_type"]').change(updateDiscountInputs);

        // Khi vào trang sửa, nếu có giá trị sẵn thì giữ nguyên, không reset
        if ($('#discount_percentage_value').val()) {
            $('#discount_percentage_value').trigger('input');
        }
        if ($('#discount_amount_value').val()) {
            $('#discount_amount_value').trigger('input');
        }
        if ($('#remaining_amount').val()) {
            $('#remaining_amount').trigger('input');
        }

        // Nếu là chế độ sửa và có discount_percentage_value, trigger sự kiện input để update lại tổng tiền
        if (window.isEditMode && $('#discount_percentage_value').val()) {
            $('#discount_percentage_value').trigger('input');
        }

        // Khi ở chế độ sửa, sau khi updateTotals, fill lại các trường thanh toán một phần từ context (dùng setTimeout để đảm bảo chạy sau updateTotals)
        if (window.isEditMode) {
            setTimeout(function() {
                if ($('#paid_amount').val()) $('#paid_amount').trigger('input');
                if ($('#remaining_amount').val()) $('#remaining_amount').trigger('input');
                if ($('#remaining_payment_due_date').val()) $('#remaining_payment_due_date').trigger('change');
            }, 200);
        }

        if (window.isEditMode && $('input[name="payment_type"]:checked').val() === 'partial') {
            showPartialPayment();
        }

        // Khi ở chế độ sửa, nếu đã có value ở remaining_amount thì gắn data-from-backend để JS không tự động ghi đè
        if (window.isEditMode && $('#remaining_amount').val() && $('#remaining_amount').val() !== '0') {
            $('#remaining_amount').data('from-backend', true);
        }

        // Hàm format số có dấu chấm ngăn cách hàng nghìn
        function formatNumberInputValue(input) {
            let val = $(input).val();
            if (!val) return;
            val = val.toString().replace(/\D/g, '');
            if (!val) return;
            $(input).val(Number(val).toLocaleString('vi-VN'));
        }

        // Hàm fill thành tiền vào input #amount (bổ sung log)
        function syncAmountInput() {
            var finalText = $('#final-amount').text();
            console.log('[DEBUG] #final-amount.text():', finalText);
            var number = finalText.replace(/\D/g, '');
            if (number) {
                var formatted = Number(number).toLocaleString('vi-VN');
                $('#total_amount').val(formatted);
                console.log('[DEBUG] Set #total_amount:', formatted);
            } else {
                $('#total_amount').val('');
                console.log('[DEBUG] Set #total_amount: (empty)');
            }
        }

        // Khi load trang, nếu #amount có value số, tự động format lại
        if ($('#total_amount').length && $('#total_amount').val()) {
            formatNumberInputValue($('#total_amount'));
        }

        // Khi chọn gói tập, ưu đãi, luôn fill lại value #amount
        $('#class_price, #discount_percentage_value, #discount_amount_value').on('change input', function() {
            setTimeout(syncAmountInput, 100);
        });

        // Khi load trang, nếu là chế độ sửa thì giữ nguyên giá trị
        if (window.isEditMode) {
            // Giữ nguyên giá trị từ backend
            if ($('#payment_amount').val()) {
                $('#payment_amount').data('from-backend', true);
            }
            if ($('#remaining_amount').val()) {
                $('#remaining_amount').data('from-backend', true);
            }
        } else {
            // Chế độ tạo mới: format lại số tiền
            if ($('#payment_amount').val()) {
                formatNumberInputValue($('#payment_amount'));
            }
            if ($('#remaining_amount').val()) {
                formatNumberInputValue($('#remaining_amount'));
            }
        }

        // Tự động set ngày thanh toán là hôm nay khi tạo mới đơn hàng
        if (!window.isEditMode && $('#payment_date').length) {
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            $('#payment_date').val(`${yyyy}-${mm}-${dd}`);
        }
    });
})(jQuery); 