import random
import threading
import queue

import aiohttp
import requests


async def read_proxies(source):
    q = queue.Queue()
    try:
        with open(source, "r") as f:
            proxies_list = [p.strip() for p in f if p.strip()]
            for p in proxies_list:
                q.put(p)
        return q

    except Exception as e:
        print(type(e))
        print(f"Error occurred while trying to open the file: {e}")
        return


async def save_valid_proxies(path_to, proxies):
    try:
        with open(path_to, "w") as f:
            f.write("\n".join(proxies))
        print(f"Finished writing {len(proxies)} valid proxies.")
    except Exception as e:
        print(type(e))
        print(f"Error occurred while trying to write to the file: {e}")


async def test_anon_proxies(session,proxy):

        try:
            response = session.get(url)
            if response.status_code == 200:
                valid_proxies.append(proxy)
                print(f"{response.status_code} Valid proxy: {proxy}")
            else:
                print(f"Invalid response {response.status_code} for proxy: {proxy}")
        except requests.RequestException as e:
            print(f"Error with proxy {proxy}: {e}")


async def gather_tasks():




async def test_auth_proxies(session,url,proxy):
    pass


async def main():

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    required_auth = True
    if required_auth:
        source_file_name = "auth_proxies.txt"
    source_file_name = "anon_proxies.txt"
    output_file_name = "valid_proxies.txt"
    base_path = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/"
    path_to_source = base_path + source_file_name
    path_to_output = base_path + output_file_name


    with aiohttp.ClientSession as session:
        valid_proxies = await test_anon_proxies(source=path_to_source,session=session)







# Write valid proxies to the output file after all threads finish
