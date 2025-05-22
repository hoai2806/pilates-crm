/**
 * JS cho trang admin điểm danh - tự động lấy gói tập phù hợp khi chọn khách hàng và buổi học
 */
(function(django) {
    'use strict';
    
    // Sử dụng jQuery từ Django admin
    var $ = django.jQuery;
    
    // Hàm cập nhật danh sách gói tập phù hợp
    function updatePackages() {
        const customerId = $('#id_customer').val();
        const classSessionId = $('#id_class_session').val();
        
        if (customerId && classSessionId) {
            // Lấy thông tin loại lớp của buổi học
            $.ajax({
                url: '/classes/api/class_session_info/',
                data: {
                    session_id: classSessionId
                },
                dataType: 'json',
                success: function(data) {
                    if (data && data.class_type_id) {
                        // Lấy gói tập phù hợp cho khách hàng và loại lớp
                        $.ajax({
                            url: '/customers/api/customer_packages/',
                            data: {
                                customer_id: customerId,
                                class_type_id: data.class_type_id
                            },
                            dataType: 'json',
                            success: function(packages) {
                                updatePackageSelect(packages);
                            }
                        });
                    }
                }
            });
        } else {
            // Reset select nếu chưa chọn đủ
            resetPackageSelect();
        }
    }
    
    // Cập nhật select gói tập
    function updatePackageSelect(packages) {
        const $select = $('#id_customer_package');
        
        // Xóa các option cũ
        $select.empty();
        
        // Thêm option trống
        $select.append($('<option value="">---------</option>'));
        
        // Thêm các gói tập vào select
        if (packages && packages.length > 0) {
            // Thêm các option
            $.each(packages, function(i, pkg) {
                const option = $('<option></option>')
                    .attr('value', pkg.id)
                    .text(`${pkg.class_type_name} - ${pkg.remaining_sessions}/${pkg.total_sessions} buổi (HSD: ${pkg.end_date || 'Không thời hạn'})`);
                
                $select.append(option);
            });
            
            // Chọn gói đầu tiên
            if (packages.length === 1) {
                $select.val(packages[0].id);
            }
        } else {
            // Hiển thị thông báo không có gói phù hợp
            $select.append($('<option disabled>Không có gói tập phù hợp</option>'));
        }
    }
    
    // Reset select gói tập
    function resetPackageSelect() {
        const $select = $('#id_customer_package');
        $select.empty();
        $select.append($('<option value="">---------</option>'));
        $select.append($('<option disabled>Chọn khách hàng và buổi học trước</option>'));
    }
    
    // Thêm sự kiện khi trang đã tải xong
    $(document).ready(function() {
        // Thêm sự kiện thay đổi cho customer và class_session
        $('#id_customer, #id_class_session').change(function() {
            updatePackages();
        });
        
        // Khởi tạo ban đầu
        updatePackages();
    });
    
})(django); 