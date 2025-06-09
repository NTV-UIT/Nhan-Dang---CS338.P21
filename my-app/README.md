# Hướng dẫn chạy Frontend (React) cho dự án StyleCLIP

## 1. Cài đặt Node.js và npm
- Đảm bảo bạn đã cài đặt Node.js (khuyến nghị >= 16.x) và npm trên hệ thống.
- Kiểm tra bằng lệnh:
  ```bash
  node -v
  npm -v
  ```

## 2. Cài đặt các package cần thiết
- Mở terminal và chuyển vào thư mục `my-app`:
  ```bash
  cd my-app
  ```
- Cài đặt các package:
  ```bash
  npm install
  ```

## 3. Chạy ứng dụng frontend
- Trong thư mục `my-app`, chạy lệnh:
  ```bash
  npm start
  ```
- Ứng dụng sẽ chạy ở địa chỉ: [http://localhost:3000](http://localhost:3000)

## 4. Kết nối với backend
- Đảm bảo backend FastAPI đã chạy ở `http://localhost:8000` (xem hướng dẫn trong `../backend/app/README.md` hoặc tài liệu dự án).
- Nếu backend chạy ở port khác, cần sửa lại URL API trong file `src/App.js` cho phù hợp.

## 5. Sử dụng giao diện
- Truy cập [http://localhost:3000](http://localhost:3000) trên trình duyệt.
- Tải ảnh lên, chọn kiểu tóc và nhấn "Chạy StyleCLIP" để nhận kết quả.

---
Nếu gặp lỗi hoặc cần hỗ trợ, hãy kiểm tra lại log terminal hoặc liên hệ người phát triển dự án.

---

# (Nội dung cũ của Create React App đã được thay thế bởi hướng dẫn sử dụng cho dự án này)
