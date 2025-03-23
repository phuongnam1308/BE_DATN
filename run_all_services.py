import subprocess
import os
import sys
import time

# Đường dẫn đến thư mục gốc chứa các dịch vụ
BASE_PATH = r"D:\AI_FITHOU\DATN\BE_DATN"
# Đường dẫn đến venv nằm ngoài BE_DATN
VENV_PATH = r"D:\AI_FITHOU\DATN\venv"

SERVICES = {
    "crawl_service": os.path.join(BASE_PATH, "crawl_service"),
    "training_service": os.path.join(BASE_PATH, "training_service"),
    "dashboard_service": os.path.join(BASE_PATH, "dashboard_service")
}

def run_service(service_name, service_path):
    print(f"Starting {service_name}...")
    try:
        # Dùng python.exe từ venv
        python_exe = os.path.join(VENV_PATH, "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            print(f"Error: Python not found at {python_exe}")
            sys.exit(1)
        # Chạy dịch vụ mà không chờ đầu ra
        process = subprocess.Popen(
            [python_exe, "main.py"],
            cwd=service_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
            universal_newlines=True
        )
        return process
    except Exception as e:
        print(f"Failed to start {service_name}: {str(e)}")
        sys.exit(1)

def monitor_service(service_name, process):
    # Đọc và in log từ stdout và stderr theo thời gian thực
    while process.poll() is None:  # Kiểm tra xem process còn chạy không
        stdout_line = process.stdout.readline()
        stderr_line = process.stderr.readline()
        if stdout_line:
            print(f"[{service_name}] {stdout_line.strip()}")
        if stderr_line:
            print(f"[{service_name} ERROR] {stderr_line.strip()}")
        time.sleep(0.1)  # Giảm tải CPU khi đọc log

def main():
    processes = []
    
    # Khởi động tất cả dịch vụ
    for service_name, service_path in SERVICES.items():
        if not os.path.exists(service_path):
            print(f"Error: Directory {service_path} does not exist!")
            sys.exit(1)
        process = run_service(service_name, service_path)
        processes.append((service_name, process))

    # Theo dõi log từ tất cả dịch vụ
    print("All services started. Monitoring logs... Press Ctrl+C to stop.")
    try:
        for service_name, process in processes:
            monitor_service(service_name, process)
    except KeyboardInterrupt:
        print("\nStopping all services...")
        for service_name, process in processes:
            print(f"Stopping {service_name}...")
            process.terminate()
            process.wait()
        print("All services stopped.")

if __name__ == "__main__":
    main()