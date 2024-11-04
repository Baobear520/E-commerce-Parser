
import asyncio

import aiohttp
from aiohttp import ClientSession

from parser.settings import PROXY_USER, PROXY_PASS
from parser.tasks.other_tasks import async_get_proxies
from parser.tasks.async_bs4_tasks import async_parse_product_data


# Function to manage concurrent parsing of multiple URLs
async def fetch_all_product_data(
        session,
        product_urls,
        use_proxy,
        require_proxy_auth,
        proxy_auth,
        proxies,
):

    tasks = [async_parse_product_data(
        session,
        url,
        use_proxy,
        require_proxy_auth,
        proxy_auth,
        proxies
    ) for url in product_urls]
    results = await asyncio.gather(*tasks)
    products = [result for result in results if result is not None]
    return products


# Main function to run the event loop
async def main():
    # Test product URLs
    product_urls = [
        "https://www.saksoff5th.com/product/current%2Felliott-faded-denim-jacket-0400021834589.html?dwvar_0400021834589_color=CANYON",
        "https://www.saksoff5th.com/product/roberto-cavalli-low-top-leather-sneakers-0400021139292.html?dwvar_0400021139292_color=WHITE_BLACK",
        "https://www.saksoff5th.com/product/hudson-jeans-blake-slim-straight-fit-corduroy-jeans-0400021517750.html?dwvar_0400021517750_color=BLACK",
        "https://www.saksoff5th.com/product/pt-torino-flat-front-pants-0400021686617.html?dwvar_0400021686617_color=STEEL"
    ]
    use_proxy = True
    require_proxy_auth = True
    proxy_auth = None
    proxies = None
    path = None

    if use_proxy:
        if use_proxy and require_proxy_auth:
            path_to_auth_proxies = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/auth_proxies.txt"
            proxy_auth = aiohttp.BasicAuth(login=PROXY_USER, password=PROXY_PASS)
            path = path_to_auth_proxies
        elif use_proxy and not require_proxy_auth:
            path_to_anon_proxies = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/anon_proxies.txt"
            path = path_to_anon_proxies
        proxies = await async_get_proxies(path)

    async with ClientSession() as session:
        try:
            parsed_products = await fetch_all_product_data(
                session,
                product_urls,
                use_proxy,
                require_proxy_auth,
                proxy_auth,
                proxies
            )
            print(f"Fetched {len(parsed_products)} products")
            # Display fetched product data
            for product in parsed_products:
                print(product)

        except Exception as e:
            print(f"Unexpected error in main: {e}")


# Call main function
if __name__ == "__main__":
    asyncio.run(main())
