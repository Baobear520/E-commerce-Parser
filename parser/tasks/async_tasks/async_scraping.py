import asyncio
from asyncio import CancelledError
from aiohttp import ClientSession

from parser.tasks.async_tasks.async_bs4_tasks import scrape_product_data
from parser.tasks.async_tasks.workers import process_tasks



async def async_scraper(input_container, use_proxy, require_proxy_auth, proxies=None):

    links = asyncio.Queue()
    products = asyncio.Queue()
    #Put all the links into an empty queue
    for p in input_container:
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
        except CancelledError:
            print("Cancelling tasks...")
            raise
        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise

def product_scraper(input_container, use_proxy, require_proxy_auth):
    try:
        return asyncio.run(async_scraper(input_container, use_proxy, require_proxy_auth))
    except KeyboardInterrupt:
        print("Manual interruption detected. Exiting...")


# Call main function
if __name__ == "__main__":
    product_urls = [
        "https://www.saksoff5th.com/product/current%2Felliott-faded-denim-jacket-0400021834589.html?dwvar_0400021834589_color=CANYON",
        "https://www.saksoff5th.com/product/roberto-cavalli-low-top-leather-sneakers-0400021139292.html?dwvar_0400021139292_color=WHITE_BLACK",
        "https://www.saksoff5th.com/product/hudson-jeans-blake-slim-straight-fit-corduroy-jeans-0400021517750.html?dwvar_0400021517750_color=BLACK",
        "https://www.saksoff5th.com/product/pt-torino-flat-front-pants-0400021686617.html?dwvar_0400021686617_color=STEEL"
    ]
    product_scraper(
        input_container=product_urls, use_proxy=False, require_proxy_auth=False
    )

