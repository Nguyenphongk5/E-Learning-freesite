# Hướng dẫn kiểm thử

Tài liệu này mô tả cách kiểm tra phiên bản E-Learning hiện có. Repo có một browser-based unit test runner không dùng thư viện cho API giỏ hàng; chưa có test framework/package runner hoặc công cụ coverage.

## Mục lục

- [1. Công nghệ và phạm vi](#1-cong-nghệ-và-phạm-vi)
- [2. Chuẩn bị môi trường](#2-chuẩn-bị-môi-trường)
- [3. Chạy website để kiểm tra thủ công](#3-chạy-website-để-kiểm-tra-thủ-công)
- [4. Test tự động](#4-test-tự-động)
- [5. Test coverage](#5-test-coverage)
- [6. Đối chiếu tiêu chí Issue #29](#6-đối-chiếu-tiêu-chí-issue-29)
- [7. Checklist kiểm thử thủ công](#7-checklist-kiểm-thử-thủ-công)
- [8. Khắc phục lỗi thường gặp](#8-khắc-phục-lỗi-thường-gặp)

## 1. Công nghệ và phạm vi

Repo hiện tại là website tĩnh, với HTML, CSS và JavaScript chạy trực tiếp trên trình duyệt. Một số trang nạp Bootstrap và các tài nguyên khác từ CDN. Không tìm thấy mã backend PHP/Python, API, database, file dependency manifest hoặc cấu hình môi trường ứng dụng trong workspace đã kiểm tra. README có nhắc đến PHP, nhưng không có mã nguồn PHP tương ứng trong repo hiện tại.

Không có test framework Jest/Vitest/Pytest/PHPUnit/Playwright/Cypress, package runner hoặc cấu hình coverage. Unit test giỏ hàng được đặt trong `tests/books-cart.test.html` và `tests/books-cart.test.js`; runner chạy trực tiếp trên trình duyệt, không cần cài package. Workflow GitHub Actions hiện có là workflow triển khai Azure Static Web Apps; workflow đó không chạy test và không tạo coverage report.

Do không có backend/database:

- Không cần khởi tạo database test hoặc seed dữ liệu.
- Website không yêu cầu biến môi trường để chạy trên máy local.
- Các tính năng phía trình duyệt có thể dùng `localStorage`; khi kiểm thử, dữ liệu lưu theo origin của trình duyệt.

## 2. Chuẩn bị môi trường

### Yêu cầu

- Trình duyệt hiện đại như Chrome, Edge hoặc Firefox.
- Python 3 nếu muốn chạy website qua HTTP local. Python chỉ dùng làm web server tĩnh, không phải dependency của ứng dụng.
- Không cần cài package bằng npm, pip, Composer hoặc công cụ tương tự để mở website.

Repo không khai báo phiên bản Python tối thiểu. Python 3.14.5 có sẵn trong môi trường thực hiện tài liệu này và hỗ trợ lệnh HTTP server bên dưới.

### Dependencies, cấu hình và dữ liệu

Không có dependencies kiểm thử bên ngoài cần cài cho browser runner, không có file `.env` cần tạo và không có database test cần chuẩn bị. Không đặt token, mật khẩu hoặc secret vào mã nguồn hay tài liệu.

Một số trang lấy thư viện, font hoặc ảnh từ CDN; cần kết nối Internet để các tài nguyên ngoài này tải được. Nếu không có mạng, chức năng chính có thể vẫn mở nhưng giao diện/tài nguyên CDN có thể thiếu.

## 3. Chạy website để kiểm tra thủ công

Từ thư mục gốc của repo, chạy:

```powershell
python -m http.server 8000
```

Lệnh này phục vụ các file tĩnh bằng HTTP ở cổng 8000; nó không chạy test tự động. Mở `http://localhost:8000/` để xem trang chính hoặc `http://localhost:8000/books/index.html` để kiểm tra thư viện sách. Dừng server bằng `Ctrl+C`.

Để chạy toàn bộ browser unit test giỏ hàng, giữ server đang chạy và mở `http://localhost:8000/tests/books-cart.test.html`. Trang tự chạy các test khi tải; tải lại trang để chạy lại toàn bộ suite. Không có tùy chọn chạy riêng từng test hoặc nhóm test. Runner dùng localStorage giả lập và hiển thị số ca đạt/thất bại trên trang, không đọc/ghi giỏ hàng thật trong browser profile.

Cú pháp lệnh đã được xác minh bằng `python -m http.server --help`. Server được chạy trong terminal có thể giữ terminal đó cho đến khi dừng.

Có thể mở file HTML trực tiếp bằng trình duyệt, nhưng HTTP local giúp kiểm tra đường dẫn tương đối và hành vi giống triển khai web hơn.

## 4. Test tự động

Repo chưa có test framework hoặc lệnh CLI như `npm test`/`pytest`. Hiện có browser unit test runner cho API giỏ hàng:

| Phạm vi | Cách chạy | Tình trạng |
| --- | --- | --- |
| Toàn bộ unit test hiện có | Chạy `python -m http.server 8000`, mở `http://localhost:8000/tests/books-cart.test.html` | Đã xác minh; trang runner báo số ca đạt/thất bại. |
| Chạy lại toàn bộ | Tải lại trang runner | Đã xác minh. |
| Chạy nhóm hoặc một test cụ thể | Chưa hỗ trợ; runner hiện chạy toàn bộ 14 ca khi tải trang. | Chưa được thiết lập. |

Các test gọi trực tiếp API `BookCart` với storage giả lập. Chúng không bao phủ giao diện DOM của trang giỏ, backend, database hoặc đăng nhập.

Khi thay đổi giao diện hoặc JavaScript, hiện có thể kiểm tra thủ công theo [Checklist kiểm thử](#7-checklist-kiểm-thử-thủ-công), đồng thời xem lỗi JavaScript trong Developer Tools của trình duyệt (tab **Console**) và lỗi tải tài nguyên trong tab **Network**.

Nếu một thao tác thất bại, tải lại trang và thử lại để phân biệt lỗi nhất thời với lỗi tái hiện được; ghi lại URL, trình duyệt, các bước thực hiện và lỗi Console. Đây là quy trình kiểm tra thủ công, không phải cơ chế tự động chạy lại test.

## 5. Test coverage

### Coverage là gì?

Coverage cho biết phần mã được thực thi khi chạy một bộ test. Các công cụ JavaScript thường báo tỷ lệ dòng lệnh, hàm, nhánh điều kiện và câu lệnh đã được thực thi. Coverage cao không tự chứng minh phần mềm không có lỗi; nó cần đi cùng test có assertion hữu ích.

### Tình trạng hiện tại

Dự án chưa có công cụ coverage. Browser unit tests hiện có không thu thập coverage. Do đó:

- Không có lệnh tạo báo cáo coverage HTML hoặc dạng khác.
- Không có thư mục báo cáo để mở và không có số liệu coverage để diễn giải.
- Không được xem bước chạy HTTP server hoặc checklist thủ công là báo cáo coverage.

### Đề xuất khi bổ sung test

Với JavaScript chạy trên trình duyệt, có thể cân nhắc bổ sung Vitest cùng V8 coverage provider sau khi repo có module/test phù hợp. Khi đó cần cấu hình test runner, phạm vi file được đo, ngưỡng (nếu có) và định dạng HTML/LCOV; sau khi cấu hình mới ghi các lệnh cài đặt, chạy test, tạo report và vị trí mở report tại đây. Chưa có cấu hình nào trong đề xuất này được cài đặt hoặc xác minh trong repo hiện tại.

## 6. Đối chiếu tiêu chí Issue #29

Các mã tiêu chí dưới đây là mã riêng để tránh trùng số với mục lục hoặc checklist. Trạng thái tài liệu không đồng nghĩa với việc dự án đã có test tự động hay coverage.

| Mã | Tiêu chí | Tình trạng tài liệu | Tình trạng triển khai/xác minh |
| --- | --- | --- | --- |
| AC-01 | Hướng dẫn chuẩn bị môi trường kiểm thử | Có hướng dẫn yêu cầu trình duyệt/Python, dependencies, biến môi trường và database (các mục không cần thiết được ghi rõ). | Lệnh Python HTTP server đã chạy và mở được trang thư viện qua localhost. Đây chỉ xác minh cách phục vụ website tĩnh, không phải thiết lập môi trường test tự động. |
| AC-02 | Hướng dẫn chạy test | Có lệnh mở browser unit test runner, hướng dẫn chạy lại, giới hạn chưa chạy riêng từng nhóm/test, cùng checklist QA thủ công. | Browser unit test giỏ hàng đã được chạy hai lượt, mỗi lượt 14 đạt/0 thất bại. Chưa có test framework, CLI runner hoặc workflow CI chạy test. |
| AC-03 | Hướng dẫn coverage | Có giải thích coverage và đề xuất Vitest/V8 cho một thay đổi tương lai. | Coverage chưa được triển khai; không có lệnh, report hoặc số liệu coverage thực tế. Đề xuất công cụ không đồng nghĩa công cụ đã được cài hoặc kiểm chứng. |

## 7. Checklist kiểm thử thủ công

- [ ] Mở `http://localhost:8000/` và kiểm tra trang chủ tải được.
- [ ] Mở `http://localhost:8000/books/index.html`; kiểm tra ảnh, CSS và các script của trang sách tải thành công.
- [ ] Thử tìm kiếm, lọc danh mục, sắp xếp và mở chi tiết sách nếu đang được hiển thị trên trang.
- [ ] Thêm sách vào giỏ; kiểm tra thông báo và badge số lượng.
- [ ] Mở trang giỏ, tải lại trang và xác nhận dữ liệu giỏ vẫn còn.
- [ ] Tăng/giảm số lượng, xóa một dòng và xóa hết; kiểm tra số lượng, thành tiền và tổng tiền.
- [ ] Thử ở kích thước desktop và cửa sổ mobile; kiểm tra không tràn ngang.
- [ ] Trong Developer Tools, xác nhận Console không có lỗi JavaScript và Network không có file nội bộ bị 404. Lỗi CDN cần được phân biệt với lỗi file trong repo.

Đây là checklist QA thủ công; nó tách biệt với browser unit test runner cho `BookCart`.

## 8. Khắc phục lỗi thường gặp

### Không chạy được lệnh `python`

Python không được cài hoặc chưa có trong `PATH`. Cài Python 3 từ nguồn phù hợp với hệ điều hành hoặc dùng lệnh launcher `py -3 -m http.server 8000` trên Windows nếu Python Launcher được cài. Lệnh `py` thay thế này chưa được xác minh trong mọi môi trường.

### Cổng 8000 đang được sử dụng

Chọn cổng khác, ví dụ:

```powershell
python -m http.server 8001
```

Sau đó mở `http://localhost:8001/`. Lệnh dùng cùng HTTP server chuẩn thư viện Python; nó không thay đổi cấu hình ứng dụng.

### Trình duyệt không mở được trang hoặc tài nguyên nội bộ bị 404

Đảm bảo terminal đang ở thư mục gốc repo khi khởi chạy server, kiểm tra URL và tên đường dẫn chính xác. Một số hệ thống triển khai phân biệt chữ hoa/chữ thường trong tên file và thư mục.

### Thiếu dependencies

Ứng dụng không khai báo dependencies cài bằng npm/pip/Composer. Nếu một tài nguyên ngoài bị thiếu, kiểm tra kết nối Internet, CDN và tab Network trước; không cài package ngẫu nhiên để thay thế.

### Thiếu biến môi trường hoặc không kết nối được database

Không có biến môi trường ứng dụng hoặc database trong cấu hình repo hiện tại. Nếu môi trường triển khai bên ngoài yêu cầu chúng, cần kiểm tra cấu hình riêng của môi trường đó; không thêm secret vào repo. Không áp dụng hướng dẫn khởi tạo database test cho phiên bản này.

### Unit test thất bại hoặc lỗi JavaScript

Đọc tên ca và lỗi hiển thị trên trang runner, xem Console của Developer Tools, rồi tải lại `tests/books-cart.test.html` để xác nhận khả năng tái hiện. Nếu lỗi liên quan thao tác giao diện, tái hiện theo checklist thủ công, kiểm tra Network và xác nhận đúng URL/port. Runner hiện không có chế độ chọn chạy một test riêng.

### Không tạo được coverage report

Đây là trạng thái hiện tại: repo đã có browser unit test cho giỏ hàng nhưng chưa cài hoặc cấu hình công cụ coverage. Vì vậy không có report để mở; cần bổ sung cấu hình coverage trong một thay đổi riêng trước khi có thể tạo báo cáo.
