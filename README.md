hướng dẫn chạy trước tiên các bạn phải tải mội trường Python /venv ( nên tải trên môi trường python 3.10 )
trước tiên các bạn phải tải google chorme và chorme driver chúng phải trùng phiên bản với nhau như của tôi là 134.xx giống nhau và làm theo giống .env
chạy trên window
-> python -m venv myenv  # Trên Windows
-> myenv\Scripts\activate
sau khi đã cài đặt môi trường thành công chúng ta tải các thư viện 
-> pip install -r requirements.txt 
khi đã tải các thư viện xong chúng ta tiến hành cd tới các file main để chạy mở 3 terminal ra để chạy vào
cd .. BEDATN/crawl_service xong đó py main.py
cd .. BEDATN/training_service xong đó py main.py
cd .. BEDATN/dashboard_service xong đó py main.py
chúng ta chạy thêm FE trong với git 
chạy npm run dev 
kết quả 
