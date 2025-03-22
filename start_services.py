import subprocess

services = {
    "Crawl Service": "cd crawl_service && uvicorn main:app --host 0.0.0.0 --port 8001 --reload",
    "Training Service": "cd training_service && uvicorn main:app --host 0.0.0.0 --port 8002 --reload",
    "Dashboard Service": "cd dashboard_service && uvicorn main:app --host 0.0.0.0 --port 8003 --reload",
    "Admin Service": "cd admin_service && uvicorn main:app --host 0.0.0.0 --port 8004 --reload",
    "API Gateway": "cd api_gateway && uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
}

processes = []
for name, command in services.items():
    print(f"Starting {name}...")
    processes.append(subprocess.Popen(command, shell=True))

for p in processes:
    p.wait()
