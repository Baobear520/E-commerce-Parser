import random
import threading
import queue
import requests

from parser.settings import TARGET_URL

q = queue.Queue()
valid_proxies = []
valid_proxies_lock = threading.Lock()  # Lock for thread-safe access to valid_proxies

source_file_name = "proxies.txt"
output_file_name = "valid_proxies.txt"
base_path = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/"
path_to_source = base_path + source_file_name
path_to_output = base_path + output_file_name

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]

# Load proxies into the queue
try:
    with open(path_to_source, "r") as f:
        proxies = [p.strip() for p in f if p.strip()]
        for p in proxies:
            q.put(p)
except Exception as e:
    print(type(e))
    print(f"Error occurred while trying to open the file: {e}")

def check_proxies():
    while not q.empty():
        proxy = q.get()
        try:
            response = requests.get(
                "http://ipinfo.io/json",
                proxies={
                    "http": proxy,
                    "https": proxy
                },
                timeout=5  # Set a timeout to avoid long waits
            )
            if response.status_code == 200:
                with valid_proxies_lock:
                    valid_proxies.append(proxy)
                print(f"{response.status_code} Valid proxy: {proxy}")
            else:
                print(f"Invalid response {response.status_code} for proxy: {proxy}")
        except requests.RequestException as e:
            print(f"Error with proxy {proxy}: {e}")




# Start threads to check proxies
threads = [threading.Thread(target=check_proxies) for _ in range(10)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

# Write valid proxies to the output file after all threads finish
try:
    with open(path_to_output, "w") as f:
        f.write("\n".join(valid_proxies))
    print(f"Finished writing {len(valid_proxies)} valid proxies.")
except Exception as e:
    print(type(e))
    print(f"Error occurred while trying to write to the file: {e}")