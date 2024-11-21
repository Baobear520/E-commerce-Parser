
import asyncio
from aiohttp import ClientSession

from parser.settings import PATH_TO_VALID_PROXIES
from parser.tasks.other_tasks import async_get_proxies
from parser.tasks.async_bs4_tasks import async_parse_product_data


# Function to manage concurrent parsing of multiple URLs
async def tasks_to_fetch_all_product_data(
        session,
        product_urls,
        use_proxy,
        require_proxy_auth,
        proxies
):

    tasks = [async_parse_product_data(
        session,
        url,
        use_proxy,
        require_proxy_auth,
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
        # "https://www.saksoff5th.com/product/roberto-cavalli-low-top-leather-sneakers-0400021139292.html?dwvar_0400021139292_color=WHITE_BLACK",
        # "https://www.saksoff5th.com/product/hudson-jeans-blake-slim-straight-fit-corduroy-jeans-0400021517750.html?dwvar_0400021517750_color=BLACK",
        # "https://www.saksoff5th.com/product/pt-torino-flat-front-pants-0400021686617.html?dwvar_0400021686617_color=STEEL"
    ]
    use_proxy = True
    require_proxy_auth = True

    if use_proxy:
        proxies = await async_get_proxies(    #
        PATH_TO_VALID_PROXIES,
        require_proxy_auth=require_proxy_auth
        )
        # Ensure proxies is a list and has entries
        if not proxies:
            print("No proxies available. Exiting.")
            return
    else:
        proxies = None

    async with ClientSession() as session:
        try:
            parsed_products = await tasks_to_fetch_all_product_data(
                session,
                product_urls,
                use_proxy,
                require_proxy_auth,
                proxies
            )

            print(f"Fetched {len(parsed_products)} products")
            # Display fetched product data
            for product in parsed_products:
                print(product)

        except Exception as e:
            print(f"Unexpected error in main: {e}")
            raise


# Call main function
if __name__ == "__main__":
    asyncio.run(main())
