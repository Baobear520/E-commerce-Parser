import asyncio

from parser.settings import MAX_WORKERS
from parser.tasks.async_tasks.other_async_tasks import get_page_text


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
        try:
            url = await input_queue.get()
            if url is None:  # Sentinel value for shutdown
                print(f"{worker_name} is shutting down...")
                break

            print(f"{worker_name} is connecting to {url} and extracting its HTML...")

            # Call the provided task function and get the result
            html = await get_page_text(
                worker_name=worker_name,
                session=session,
                url=url,
                use_proxy=use_proxy,
                require_proxy_auth=require_proxy_auth,
                proxies=proxies
            )
            if not html:
                raise ValueError(f"Failed to fetch valid content from {url}")

            print(f"{worker_name} is scraping {url}...")
            result = await task_func(html)

            if isinstance(result,dict): #iterate through the items if the result is a dictionary (scrape_title_and_upc task)
                result = result.items()
            for r in result:
                output_queue.put_nowait(r)

        except ValueError as e:
            print(f"{worker_name} encountered an error: {e}")
            raise
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
    # Start workers
    tasks = [
        asyncio.create_task(
            worker(
                session,
                input_queue,
                output_queue,
                task_func,
                f"Worker {i + 1}",
                use_proxy,
                require_proxy_auth,
                proxies
            )
        ) for i in range(MAX_WORKERS)
    ]

    try:
        # Wait for all tasks to be processed
        await input_queue.join()

    finally:
        # Send shutdown signals to workers
        for _ in range(MAX_WORKERS):
            input_queue.put_nowait(None)

        # Await worker completion
        await asyncio.gather(*tasks, return_exceptions=True)