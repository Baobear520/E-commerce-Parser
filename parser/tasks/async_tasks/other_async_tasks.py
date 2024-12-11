import asyncio
import random

import aiofiles
import aiohttp
from other_scripts.exceptions import AccessDeniedException, MaxRetriesExceeded
from parser.settings import MAX_RETRIES, DELAY, USER_AGENT, TIMEOUT
from other_scripts.test_proxies import check_proxies, parse_proxy


async def async_get_proxies(source, require_proxy_auth=False, update_proxy_source=False):

    if update_proxy_source:
        await check_proxies(has_proxy_auth=require_proxy_auth)  # write valid proxies to source file
    try:
        # Open the file asynchronously and read proxies line-by-line
        async with aiofiles.open(source, "r") as f:
            proxies = [line.strip() for line in await f.readlines() if line.strip()]
            print("Obtained a list of proxies from the existing file.")
        return proxies
    except Exception as e:
        print(type(e).__name__)
        print(f"Error while extracting proxies from the file: {e}")
        return []


async def get_page_text(
        worker_name,
        session,
        url,
        use_proxy,
        require_proxy_auth,
        proxies,
        max_retries=MAX_RETRIES,
        initial_delay=DELAY,

):
    headers = {"User-Agent": USER_AGENT}
    retries = 1
    proxy_auth = None
    while retries < max_retries:
        if use_proxy:
            proxy = random.choice(proxies)
            if require_proxy_auth:
                proxy, login, password = await parse_proxy(proxy=proxy)
                proxy_auth = aiohttp.BasicAuth(login=login, password=password)

        try:
            async with session.get(
                    url=url,
                    headers=headers,
                    proxy=proxy if proxy else None,
                    proxy_headers=headers,
                    proxy_auth=proxy_auth,
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as response:
                if response.status != 200:
                    print(f"{worker_name}: Invalid response from {url}: {response.status}")
                    return
                text = await response.text()
                if "Access denied" in text:
                    raise AccessDeniedException
                return text

        except AccessDeniedException:
            if not use_proxy:
                print(f"{worker_name}: Access denied.")
            else:
                print(f"{worker_name}: Access denied with proxy {proxy}.")
                proxies = [p for p in proxies if not p.startswith(proxy)]

        except asyncio.TimeoutError:
            print(f"{worker_name}: Timeout error while trying to obtain the page's text from {url}.\nRetrying {retries}/{max_retries}...")
            retries += 1
            await asyncio.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff

        except aiohttp.ClientError:
            if use_proxy:
                proxies = [p for p in proxies if not p.startswith(proxy)]

        except Exception as e:
            print(f"{worker_name}: Unexpected error: {type(e).__name__}, {e}")

    # If all retries fail
    raise MaxRetriesExceeded(url)


async def mock_products_scraper(number_of_products,start):
    products = {}
    for i in range(start,start+number_of_products):
        product = {
            "name": None,
            "brand_name": None,
            "description": None,
            "original_price_USD": None,
            "discount_price_USD": None,
            "color": None,
            "style_code": None
        }
        products.update({i+1: product})
        #print(f"Added product {i+1}")
    await asyncio.sleep(5)
    print(f"Returning {len(products)} objects")
    return products


# async def download_proxy_list(url):
#     async with aiohttp.ClientSession() as session:
#         result = await session.get(url)
#         print(result)
#
#         #await save_valid_proxies(path_to=,proxies=result)
#
#
# if __name__ == "__main__":
#     asyncio.run(download_proxy_list(
#         url="https://free-proxy-list.net/blog/get-proxy-list-using-api?https=no&anonymity=yes,"
#     ))