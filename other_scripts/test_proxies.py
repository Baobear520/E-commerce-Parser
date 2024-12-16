import asyncio
import os

import aiohttp
import aiofiles
import random

from parser.settings import PATH_TO_VALID_PROXIES, USER_AGENT, TIMEOUT, BASE_DIR



async def read_proxies(source):
    """
    Load proxies from a file asynchronously and place them into a list.
    Returns a list of proxies with both http:// and https:// variants.
    """
    proxies = []
    try:
        async with aiofiles.open(source, "r") as f:
            async for line in f:
                proxies.append(line.strip())
    except Exception as e:
        print(f"Error loading proxies from file '{source}': {e}")

    finally:
        return proxies  # Return an empty list in case of an error


async def save_valid_proxies(path_to, proxies):
    """Save valid proxies to a file asynchronously."""
    try:
        async with aiofiles.open(path_to, "w") as f:
            await f.write("\n".join(proxies))
        print(f"Finished writing {len(proxies)} valid proxies.")
    except Exception as e:
        print(f"Error writing valid proxies to file: {e}")


async def parse_proxy(proxy):
    host, port, login, password = proxy.split(":")
    return host, port, login, password

async def test_proxy(session, url, proxy, has_proxy_auth):
    """Test a proxy by attempting to connect to a URL."""
    headers = {"User-Agent": USER_AGENT}
    protocols = ["http", "https"]
    try:
        if has_proxy_auth:
            host, port, login, password = await parse_proxy(proxy=proxy)
            proxy_auth = aiohttp.BasicAuth(login=login, password=password)
        else:
            proxy_auth = None
        for protocol in protocols:
            proxy = f"{protocol}://{proxy}"
            async with session.get(
                    url,
                    proxy=proxy,
                    proxy_headers=headers,
                    proxy_auth=proxy_auth,
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as response:
                if response.status == 200:
                    print(f"Valid proxy: {proxy}")
                    return proxy if not has_proxy_auth else ":".join([host,port,login,password])

                else:
                    print(f"Invalid response {response.status} for proxy: {proxy}")
    except Exception as e:
        print(f"Error with proxy {proxy}: {type(e).__name__}\n{e}")


async def gather_tasks(session, url, proxies_queue, has_proxy_auth):
    """Gather and run tasks to test proxies concurrently."""
    tasks = []
    while not proxies_queue.empty():
        proxy = await proxies_queue.get()
        task = test_proxy(session, url, proxy, has_proxy_auth)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return [proxy for proxy in results if proxy]


async def check_proxies(has_proxy_auth=False):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    source_file_name = "auth_proxies.txt" if has_proxy_auth else "anon_proxies.txt"
    base_path = os.path.join(BASE_DIR, "data")
    path_to_source = "/".join([base_path, source_file_name])
    path_to_output = PATH_TO_VALID_PROXIES
    test_url = "https://httpbin.org/ip"
    proxies_queue = asyncio.Queue()

    #Read proxies from file
    proxies_list = await read_proxies(source=path_to_source)
    if not proxies_list:
        print("No proxies to test.")
        return
    for p in proxies_list:
        proxies_queue.put_nowait(p)

    async with aiohttp.ClientSession(headers={"User-Agent": random.choice(user_agents)}) as session:
        valid_proxies = await gather_tasks(session, test_url, proxies_queue, has_proxy_auth)

    if valid_proxies:
        await save_valid_proxies(path_to=path_to_output, proxies=valid_proxies)
    else:
        print("No valid proxies found.")


if __name__ == "__main__":
    asyncio.run(check_proxies())

