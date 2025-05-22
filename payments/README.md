# Module Quản lý Đơn hàng - HDCRM

Module Quản lý Đơn hàng cung cấp các tính năng quản lý đơn hàng, hóa đơn và thanh toán cho hệ thống HDCRM. Module này bao gồm cả giao diện Admin nâng cao và các trang frontend dành cho nhân viên.

## Tính năng chính

### Quản lý đơn hàng
- Tạo đơn hàng mới với thông tin khách hàng, dịch vụ, giá cả
- Áp dụng khuyến mãi (theo % hoặc số tiền cụ thể)
- Tự động tạo số hóa đơn theo quy tắc
- Theo dõi trạng thái đơn hàng (đang chờ, hoàn thành, thất bại, hoàn tiền)
- Tạo gói tập tự động khi tạo đơn hàng

### Báo cáo doanh thu
- Báo cáo tổng quan doanh thu theo tháng/quý/năm
- Biểu đồ trực quan hóa doanh thu
- Thống kê theo phương thức thanh toán
- Thống kê theo loại dịch vụ
- Thống kê lợi nhuận (doanh thu - chi phí)

### Xuất dữ liệu
- Xuất danh sách đơn hàng ra định dạng CSV
- Lọc dữ liệu xuất theo khoảng thời gian
- Tùy chỉnh các trường thông tin xuất ra

## Cách sử dụng

### Truy cập module
- **Admin**: Truy cập tại `/admin/payments/payment/`
- **Frontend**: Truy cập tại `/payments/` hoặc `/hdcrm/don-hang/`

### Tạo đơn hàng mới
1. Truy cập `/payments/them-moi/`
2. Điền thông tin khách hàng, dịch vụ và giá tiền
3. Áp dụng khuyến mãi nếu cần
4. Chọn phương thức thanh toán và trạng thái
5. Lưu đơn hàng

### Xem báo cáo doanh thu
1. Truy cập `/admin/payments/payment/`
2. Nhấn nút "Báo cáo doanh thu"
3. Chọn khoảng thời gian (tháng/quý/năm)
4. Xem biểu đồ và thống kê

### Xuất dữ liệu
1. Truy cập `/payments/`
2. Thiết lập các bộ lọc (ngày, trạng thái...)
3. Nhấn nút "Xuất CSV"

## Liên kết với các module khác

### Gói tập
- Mỗi đơn hàng có thể tự động tạo gói tập
- Gói tập được liên kết với đơn hàng qua trường `payment`
- Thông tin đơn hàng được hiển thị trong chi tiết gói tập

### Khách hàng
- Mỗi đơn hàng được liên kết với một khách hàng
- Lịch sử đơn hàng hiển thị trong trang chi tiết khách hàng

## Lưu ý
- Các đơn hàng đã hoàn thành không nên chỉnh sửa thông tin số tiền
- Cần cập nhật trạng thái đơn hàng khi thanh toán thành công
- Báo cáo doanh thu chỉ tính các đơn hàng có trạng thái "Hoàn thành" 