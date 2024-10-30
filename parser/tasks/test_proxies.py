import threading
import queue
import requests

q = queue.Queue()
valid_proxies = []
valid_proxies_lock = threading.Lock()  # Lock for thread-safe access to valid_proxies

source_file_name = "proxies.txt"
output_file_name = "valid_proxies.txt"
base_path = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/"
path_to_source = base_path + source_file_name
path_to_output = base_path + output_file_name

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
    print("Finished writing valid proxies.")
except Exception as e:
    print(type(e))
    print(f"Error occurred while trying to write to the file: {e}")