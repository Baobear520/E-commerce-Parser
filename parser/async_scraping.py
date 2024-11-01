
import random
import asyncio
import time

from aiohttp import ClientSession, ServerDisconnectedError

from parser.settings import TARGET_URL
from parser.tasks.other_tasks import async_get_proxies
from parser.tasks.selenium_tasks import scroll_to_pagination, scrape_product_links
from parser.tasks.bs4_tasks import parse_product_data, async_parse_product_data


# Function to manage concurrent parsing of multiple URLs
async def fetch_all_product_data(session, product_urls,proxies):

    tasks = [async_parse_product_data(session, url, proxies) for url in product_urls]
    results = await asyncio.gather(*tasks)
    products = [result for result in results if result is not None]
    return products


# Main function to run the event loop
async def main():
    # Example product URLs
    product_urls = [
        "https://www.saksoff5th.com/product/current%2Felliott-faded-denim-jacket-0400021834589.html?dwvar_0400021834589_color=CANYON",
        "https://www.saksoff5th.com/product/roberto-cavalli-low-top-leather-sneakers-0400021139292.html?dwvar_0400021139292_color=WHITE_BLACK",
        "https://www.saksoff5th.com/product/hudson-jeans-blake-slim-straight-fit-corduroy-jeans-0400021517750.html?dwvar_0400021517750_color=BLACK",
        "https://www.saksoff5th.com/product/pt-torino-flat-front-pants-0400021686617.html?dwvar_0400021686617_color=STEEL"
    ]
    path_to_proxies = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/valid_proxies.txt"
    proxies = await async_get_proxies(source=path_to_proxies)  # Load proxies list

    async with ClientSession() as session:
        # Use Selenium to set up cookies
        try:
            parsed_products = await fetch_all_product_data(session,product_urls, proxies)
            print(f"Fetched {len(parsed_products)} products")
            # Display fetched product data
            for product in parsed_products:
                print(product)
        except ServerDisconnectedError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(type(e))
            print(f"Error: {str(e.args)}")


# Call main function
if __name__ == "__main__":
    asyncio.run(main())
