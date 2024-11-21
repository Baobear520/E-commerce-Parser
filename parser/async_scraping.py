import asyncio
import random
import time

import aiohttp
from aiohttp import ClientSession

from parser.exceptions import AccessDeniedException
from parser.settings import USER_AGENT, PATH_TO_VALID_PROXIES, MAX_WORKERS, MAX_RETRIES, DELAY, TIMEOUT
from parser.tasks.async_bs4_tasks import scrape_product_data
from parser.tasks.other_tasks import async_get_proxies
from parser.tasks.test_proxies import trim_proxy


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
                proxy, login, password = await trim_proxy(proxy=proxy)
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
                #print(f"Connected to {url}")
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
            retries += 1
            await asyncio.sleep(10)

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"{worker_name}: {type(e).__name__}, {e}.\nRetrying {retries}/{max_retries}")
            if use_proxy:
                proxies = [p for p in proxies if not p.startswith(proxy)]
            retries += 1
            await asyncio.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff

        except Exception as e:
            print(f"{worker_name}: Unexpected error: {type(e).__name__}, {e}")
            retries += 1
            await asyncio.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff

    print(f"{worker_name}: max retries reached for {url}. Terminating the worker.")
    return

async def worker(
        session,
        input_queue,
        output_queue,
        task_func,
        use_proxy,
        require_proxy_auth,
        proxies,
        worker_name
):
    while True:
        url = await input_queue.get()
        try:
            # Call the provided task function and get the result
            print(f"{worker_name} is scraping {url}...")
            html = await get_page_text(
                session=session,
                url=url,
                use_proxy=use_proxy,
                require_proxy_auth=require_proxy_auth,
                proxies=proxies,
                worker_name=worker_name
            )
            if html:
                result = await task_func(html)
                input_queue.task_done()
                if isinstance(result,dict): #iterate through the items if the result is a dictionary (scrape_title_and_upc task)
                    result = result.items()
                for r in result:
                    output_queue.put_nowait(r)

        except Exception as e:
            print(f"{worker_name} failed processing {url}: {type(e).__name__}, {e}")
        finally:
            input_queue.task_done()

async def process_tasks(
    session,
    input_queue,
    output_queue,
    task_func,
    use_proxy,
    require_proxy_auth,
    proxies
):
    # Create worker tasks to process the queue concurrently.
    tasks = []
    for i in range(MAX_WORKERS):
        tasks.append(
            asyncio.create_task(
                worker(
                    session,
                    input_queue,
                    output_queue,
                    task_func,
                    use_proxy,
                    require_proxy_auth,
                    proxies,
                    worker_name=f"Worker {i + 1}"
                )
            )
        )
    # Cancel worker tasks.
    try:
        await input_queue.join()
    except asyncio.CancelledError:
        print("Tasks were cancelled. Shutting down gracefully.")
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    use_proxy = True
    require_proxy_auth = False
    if use_proxy:
        proxies = await async_get_proxies(
            PATH_TO_VALID_PROXIES,
            require_proxy_auth=require_proxy_auth,
            update_proxy_source=True
        )
        # Ensure proxies is a list and has entries
        if not proxies:
            print("No proxies available. Switching to no-proxy mode.")
            use_proxy = False
            require_proxy_auth = False
            proxies = None

    start_time = time.time()
    links = asyncio.Queue()
    products = asyncio.Queue()
    # Test product URLs
    product_urls = [
        "https://www.saksoff5th.com/product/current%2Felliott-faded-denim-jacket-0400021834589.html?dwvar_0400021834589_color=CANYON",
        "https://www.saksoff5th.com/product/roberto-cavalli-low-top-leather-sneakers-0400021139292.html?dwvar_0400021139292_color=WHITE_BLACK",
        "https://www.saksoff5th.com/product/hudson-jeans-blake-slim-straight-fit-corduroy-jeans-0400021517750.html?dwvar_0400021517750_color=BLACK",
        "https://www.saksoff5th.com/product/pt-torino-flat-front-pants-0400021686617.html?dwvar_0400021686617_color=STEEL"
    ]
    for p in product_urls:
        await links.put(p)

    async with ClientSession() as session:
        try:
            # Create a loop with concurrent tasks to process products and scrape data
            await process_tasks(
                session=session,
                input_queue=links,
                output_queue=products,
                task_func=scrape_product_data,
                use_proxy=use_proxy,
                require_proxy_auth=require_proxy_auth,
                proxies=proxies
            )

        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise
        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            # Convert to hours, minutes, seconds, and milliseconds
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            milliseconds = int((elapsed_time % 1) * 1000)

            # Display runtime
            print(f"Runtime: {hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}")


# Call main function
if __name__ == "__main__":
    asyncio.run(main())
