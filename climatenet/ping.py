import os
import time
from datetime import datetime
from ping3 import ping, verbose_ping

def main():
    site = "google.com"
    desktop_path = os.path.expanduser("/home/ubuntu")
    log_file_path = os.path.join(desktop_path, "ping_log.log")
    
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write("Ping Log\n")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response_time = ping(site)
        
        if response_time is not None:
            result = f"{timestamp} - Website: {site} - Response time: {response_time:.3f} ms\n"
        else:
            result = f"{timestamp} - Ping failed\n"
        
        with open(log_file_path, "a") as log_file:
            log_file.write(result)
        
        print(result)
        time.sleep(10)

if __name__ == "__main__":
    main()
