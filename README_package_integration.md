# Hướng dẫn kết nối gói tập với đơn hàng và quản lý trừ số buổi tập

## Kết nối gói tập với đơn hàng

Hệ thống HDCRM cho phép kết nối gói tập với đơn hàng để theo dõi thanh toán và số buổi tập. Các bước thực hiện như sau:

1. Khi tạo hoặc chỉnh sửa gói tập, chọn đơn hàng tương ứng từ danh sách.
2. Đơn hàng và gói tập sẽ được liên kết với nhau thông qua trường `payment` trong model `CustomerPackage`.
3. Thông tin về đơn hàng được hiển thị trong các báo cáo và các trang xem chi tiết gói tập.

## Cơ chế trừ số buổi tập

Hệ thống tự động trừ số buổi tập thông qua quá trình điểm danh:

1. Khi học viên tham gia buổi học và được điểm danh, hệ thống sẽ tự động tìm gói tập phù hợp để trừ số buổi.
2. Ưu tiên sử dụng gói tập cùng loại lớp và sắp hết hạn trước.
3. Chỉ gói tập ở trạng thái "Đang sử dụng" (active) và có số buổi còn lại > 0 mới được sử dụng.
4. Khi điểm danh, hệ thống gọi phương thức `use_session()` của model `CustomerPackage` để giảm số buổi còn lại.
5. Khi số buổi còn lại bằng 0, gói tập sẽ tự động chuyển sang trạng thái "Đã dùng hết buổi" (used_up).
6. Thông tin về gói tập được sử dụng sẽ được lưu trong bản ghi điểm danh để tiện theo dõi.

## Tầm quan trọng của ngày bắt đầu và ngày kết thúc

- **Ngày bắt đầu**: Xác định thời điểm học viên có thể bắt đầu sử dụng gói tập. Điều này đặc biệt quan trọng khi học viên đăng ký trước nhưng chỉ bắt đầu tập luyện sau một thời gian.
- **Ngày kết thúc**: Xác định thời điểm gói tập hết hạn. Nếu để trống, gói tập sẽ không có thời hạn cụ thể và chỉ kết thúc khi hết số buổi tập.

## Kiểm tra và theo dõi

- Thông tin về việc sử dụng gói tập có thể được xem trong mục "Điểm danh liên quan" của trang chi tiết khách hàng.
- Các gói tập đã được sử dụng hết hoặc hết hạn sẽ tự động chuyển trạng thái, giúp dễ dàng theo dõi và quản lý.
- Báo cáo về tình trạng sử dụng gói tập có thể được tạo từ dữ liệu điểm danh và thông tin gói tập. 