document.addEventListener('DOMContentLoaded', function() {
    // Hàm để kiểm tra xem có phải trang admin hợp lệ để thêm sidebar không
    function isAdminPage() {
        if (document.body.classList.contains('login-page') || 
            document.body.classList.contains('popup') || // SimpleUI dùng class 'popup' cho trang popup
            (window.opener && window.opener !== window)) {
            return false;
        }
        // Kiểm tra xem #app (container chính của SimpleUI) có tồn tại không
        return document.getElementById('app') !== null;
    }

    if (!isAdminPage()) {
        return; // Không thêm sidebar trên trang login, popup, hoặc trang không phải SimpleUI admin
    }

    // Tạo div cho right sidebar
    const rightbar = document.createElement('div');
    rightbar.id = 'custom-admin-rightbar';

    // Xác định admin path một cách tương đối an toàn hơn
    let adminPath = '/admin/'; // Mặc định
    const adminLinks = document.querySelectorAll('a[href*="/logout/"], a[href*="/password_change/"]');
    let potentialAdminPath = null;

    for (let i = 0; i < adminLinks.length; i++) {
        const href = adminLinks[i].getAttribute('href');
        if (href && href.startsWith('/')) {
            if (href.includes('/logout/')) {
                potentialAdminPath = href.substring(0, href.indexOf('/logout/') + 1);
                break;
            }
            if (href.includes('/password_change/')) {
                potentialAdminPath = href.substring(0, href.indexOf('/password_change/') + 1);
                break;
            }
        }
    }
    if (potentialAdminPath) {
        adminPath = potentialAdminPath;
    }
    
    // Đảm bảo adminPath kết thúc bằng dấu /
    if (!adminPath.endsWith('/')) {
        adminPath += '/';
    }

    // Nội dung HTML cho sidebar
    rightbar.innerHTML = `
        <h4>Điều hướng nhanh</h4>
        <ul>
            <li><a href="${adminPath}">Trang chủ Admin</a></li>
            <li><a href="${adminPath}customers/customer/">Khách hàng</a></li>
            <li><a href="${adminPath}classes/classschedule/">Lịch học</a></li>
            <li><a href="${adminPath}classes/classtype/">Loại lớp học</a></li>
            <li><a href="${adminPath}branches/branch/">Chi nhánh</a></li>
            <li><a href="${adminPath}instructors/instructor/">Giáo viên</a></li>
            <li><a href="${adminPath}payments/expense/">Chi phí</a></li>
            <li><a href="${adminPath}auth/user/">Người dùng</a></li>
            <li><a href="${adminPath}auth/group/">Nhóm quyền</a></li>
        </ul>
    `;

    function tryAppendRightbar() {
        const appContainer = document.getElementById('app');
        // Chờ #main-content (el-main của simpleUI) xuất hiện
        const mainContent = document.getElementById('main-content'); 

        if (appContainer && mainContent) {
            document.body.appendChild(rightbar);
            // console.log('Right sidebar appended.');
        } else {
            // Nếu #app hoặc #main-content chưa sẵn sàng, thử lại sau một chút
            // console.log('#app or #main-content not ready, retrying...');
            requestAnimationFrame(tryAppendRightbar); // Thử lại ở frame tiếp theo
        }
    }

    // Bắt đầu thử chèn rightbar
    requestAnimationFrame(tryAppendRightbar);
}); 