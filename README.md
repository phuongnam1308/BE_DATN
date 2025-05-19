Hướng Dẫn Chạy Dự Án
1. Cài Đặt Môi Trường Python
Trước tiên, bạn cần cài đặt Python 3.10 trên hệ thống của mình. Bạn có thể tải Python từ python.org.
Sau khi cài đặt Python, tạo một môi trường ảo để quản lý các thư viện của dự án:
python -m venv myenv

Kích hoạt môi trường ảo trên Windows:
myenv\Scripts\activate

2. Cài Đặt Google Chrome và ChromeDriver
Bạn cần cài đặt Google Chrome trên máy tính. Ngoài ra, tải ChromeDriver với phiên bản khớp với Chrome của bạn (ví dụ: phiên bản 134.xx của tôi). Tải ChromeDriver tại chromedriver.chromium.org.
Hãy đảm bảo cấu hình file .env theo yêu cầu của dự án.
3. Cài Đặt Các Thư Viện
Sau khi kích hoạt môi trường ảo thành công, cài đặt các thư viện cần thiết bằng lệnh sau:
pip install -r requirements.txt

4. Chạy Các Dịch Vụ
Dự án yêu cầu chạy ba dịch vụ riêng biệt. Mở ba cửa sổ terminal và thực hiện như sau:

Đối với dịch vụ crawl:

cd BEDATN/crawl_service
python main.py


Đối với dịch vụ training:

cd BEDATN/training_service
python main.py


Đối với dịch vụ dashboard:

cd BEDATN/dashboard_service
python main.py

5. Chạy Frontend
Ngoài các dịch vụ backend, bạn cần chạy phần frontend. Di chuyển đến thư mục frontend và chạy lệnh:
npm run dev

6. Kết Quả
Khi tất cả các dịch vụ và frontend đã chạy, dự án sẽ hoạt động như mong đợi. Kiểm tra output trên terminal để phát hiện lỗi hoặc nhận thêm hướng dẫn nếu có


# Dự án của tôi

Ảnh các kết quả crawl :
![Ảnh kết quả crawl](https://github.com/phuongnam1308/BE_DATN/blob/main/kqloccrawl.pdf)

Ảnh kết quả tay :
![Ảnh kết quả nhập tay](https://github.com/phuongnam1308/BE_DATN/blob/main/ketquatesttay.png)

Video có chứa dẩy đủ hướng dẫn https://drive.google.com/drive/folders/1EGpmEz0vCYQdw9ZMR86JwbXE2bDtMhIk?usp=sharing
