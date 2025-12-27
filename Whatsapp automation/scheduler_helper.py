# scheduler_helper.py
import subprocess
import os

def register_windows_task(task_id, run_time, phone, message, file_path):
    # Command: schtasks /create /tn "WhatsAppTask_{id}" /tr "python.exe worker.py ..." /sc once /st HH:mm
    python_path = os.sys.executable
    worker_path = os.path.abspath("worker.py")
    
    cmd = [
        'schtasks', '/create', '/f',
        '/tn', f"WhatsAppTask_{task_id}",
        '/tr', f'"{python_path}" "{worker_path}" {phone} "{message}" "{file_path}"',
        '/sc', 'ONCE',
        '/st', run_time # Format HH:mm
    ]
    subprocess.run(cmd, check=True)

def cancel_task(task_id):
    subprocess.run(['schtasks', '/delete', '/tn', f"WhatsAppTask_{task_id}", '/f'])
