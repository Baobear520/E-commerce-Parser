import random
import asyncio
import json

import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientResponseError, ServerDisconnectedError, ClientError
from aiohttp.http_exceptions import HttpProcessingError

from parser.exceptions import AccessDeniedException
from parser.settings import USER_AGENT

from parser.tasks.test_proxies import trim_proxy


# async def async_get_page_soup(response):
#     # Process page content
#     page_content = await response.text()
#     return BeautifulSoup(page_content, 'lxml')


async def async_parse_product_data(
        session: ClientSession,
        url: str,
        use_proxy,
        require_proxy_auth,
        proxies):

    """Asynchronously parses the HTML of a product page and extracts product information."""
    headers = {"User-Agent": USER_AGENT}

    max_retries = 5
    retry_count = 1
    while retry_count < max_retries:
        proxy = None
        if use_proxy:
            proxy = random.choice(proxies)
            if require_proxy_auth:
                proxy, login, password = await trim_proxy(proxy=proxy)
                proxy_auth = aiohttp.BasicAuth(login=login, password=password)
        else:
            proxies = None
            proxy_auth = None
        try:
            print(proxy)
            async with session.get(
                    url=url,
                    headers=headers,
                    proxy=proxy,
                    proxy_auth=proxy_auth,
                    timeout=10
            ) as response:
                soup = await async_get_page_soup(response=response)
                # Check if the page title is "Access Denied"
                if soup.title and "Access Denied" in soup.title.get_text():
                    raise AccessDeniedException

        except AccessDeniedException:
            print(f"Access denied.")
            if use_proxy:
                proxies = [p for p in proxies if not p.startswith(proxy)]
            if retry_count == max_retries:
                print("Reached maximum number of retries. Closing...")
                return
            else:
                retry_count += 1
                await asyncio.sleep(10)
                continue

        except (ClientResponseError,
            ClientError,
            ServerDisconnectedError,
            HttpProcessingError) as e:

            print(
                f"Couldn't establish connection:\
                {type(e).__name__, e}.\nRetrying {retry_count}/{max_retries}"
            )
            if retry_count == max_retries:
                print("Reached maximum number of retries. Closing...")
                return
            else:
                retry_count += 1
                await asyncio.sleep(10)
                continue

        except Exception as e:
            print(type(e))
            print(f"Non-aiohttp exception occurred: {getattr(e, "__dict__", {})}.\nRetrying {retry_count}/{max_retries}")
            if retry_count == max_retries:
                print("Reached maximum number of retries. Closing...")
                return
            else:
                retry_count += 1
                await asyncio.sleep(10)
                continue


        else: #if no exceptions occurred during connection to url
            product_container = soup.find('div', class_='product-secondary-section pdp-standard')
            if not product_container:
                print("Product container not found.")
                return None
            print("Found the item container")

            # Initialize product data dictionary
            product = {
                "name": None,
                "brand_name": None,
                "description": None,
                "original_price_USD": None,
                "discount_price_USD": None,
                "color": None,
                "style_code": None
            }

            # Extract brand name
            try:
                # Извлекаем бренд
                brand_tag = soup.find('span', class_='product-brand-name')
                if brand_tag:
                    brand_link = brand_tag.find('a')
                    product["brand_name"] = brand_link.get_text(strip=True) if brand_link else None

                # Извлекаем название продукта
                name_tag = soup.find('span', class_='product-name h2')
                if name_tag:
                    product["name"] = name_tag.get_text(strip=True)

                # Извлекаем описание
                description_tag = soup.find('div', class_='value content', id='collapsible-details-1')
                if description_tag:
                    description = description_tag.get_text(strip=True).split(".")[0] + "."
                    product["description"] = description

                # Locate the prices container
                prices_container = soup.find('div', class_='prices')

                if prices_container:
                    # Extract the original price
                    original_price_tag = prices_container.find('span', class_='value')
                    product["original_price_USD"] = (
                        float(original_price_tag['content'].replace(',', ''))
                        if original_price_tag and original_price_tag.has_attr('content')
                        else None
                    )

                    # Extract the discount price
                    discount_price_tag = prices_container.find('span', class_='value bfx-price')
                    product["discount_price_USD"] = (
                        float(discount_price_tag['content'].replace(',', ''))
                        if discount_price_tag and discount_price_tag.has_attr('content')
                        else None
                    )

                # Извлекаем цвет (массив)
                colors = []

                # Проверяем наличие единственного цвета
                single_color_container = soup.find('span', class_='color non-input-label attribute-single')
                if single_color_container:
                    color_tag = single_color_container.find('span', class_='text2')
                    if color_tag:
                        colors.append(color_tag.get_text(strip=True).lower())

                # Ищем элемент с множественными цветами
                multi_color_container = soup.find('ul', class_='color-wrapper radio-group-list', role='radiogroup')
                if multi_color_container:
                    color_buttons = multi_color_container.find_all('button', class_='color-attribute')
                    for button in color_buttons:
                        aria_label = button.get('aria-label', '')
                        if 'Select Color' in aria_label:
                            color_name = aria_label.split('Select Color')[-1].strip()
                            colors.append(color_name.lower())

                # Устанавливаем значение массива цветов или None, если цветов нет
                product["color"] = colors if colors else None

                # Устанавливаем значение массива цветов или None, если цветов нет
                # Конвертируем в JSON-string
                product["color"] = json.dumps(colors) if colors else None

                # Извлекаем Style Code
                style_code_tag = soup.find('div', class_='product-detail-id')
                if style_code_tag:
                    style_code_text = style_code_tag.get_text(strip=True)
                    if "Style Code:" in style_code_text:
                        product["style_code"] = style_code_text.split("Style Code:")[-1].strip()

                await asyncio.sleep(3)
                return product  # Successful parse


            except Exception as e:
                print(f"Unexpected error while parsing data: {getattr(e, "__dict__", {})}.")
                await asyncio.sleep(1)
                return product



async def scrape_product_data(html):
    # Initialize product data dictionary
    product = {
        "name": None,
        "brand_name": None,
        "description": None,
        "original_price_USD": None,
        "discount_price_USD": None,
        "color": None,
        "style_code": None
    }

    try:
        soup = BeautifulSoup(html, 'lxml')
        product_container = soup.find('div', class_='product-secondary-section pdp-standard')
        if not product_container:
            print("Product container not found.")
            return None
        print("Found the item container")

        # Извлекаем бренд
        brand_tag = soup.find('span', class_='product-brand-name')
        if brand_tag:
            brand_link = brand_tag.find('a')
            product["brand_name"] = brand_link.get_text(strip=True) if brand_link else None

        # Извлекаем название продукта
        name_tag = soup.find('span', class_='product-name h2')
        if name_tag:
            product["name"] = name_tag.get_text(strip=True)

        # Извлекаем описание
        description_tag = soup.find('div', class_='value content', id='collapsible-details-1')
        if description_tag:
            description = description_tag.get_text(strip=True).split(".")[0] + "."
            product["description"] = description

        # Locate the prices container
        prices_container = soup.find('div', class_='prices')

        if prices_container:
            # Extract the original price
            original_price_tag = prices_container.find('span', class_='value')
            product["original_price_USD"] = (
                float(original_price_tag['content'].replace(',', ''))
                if original_price_tag and original_price_tag.has_attr('content')
                else None
            )

            # Extract the discount price
            discount_price_tag = prices_container.find('span', class_='value bfx-price')
            product["discount_price_USD"] = (
                float(discount_price_tag['content'].replace(',', ''))
                if discount_price_tag and discount_price_tag.has_attr('content')
                else None
            )

        # Извлекаем цвет (массив)
        colors = []

        # Проверяем наличие единственного цвета
        single_color_container = soup.find('span', class_='color non-input-label attribute-single')
        if single_color_container:
            color_tag = single_color_container.find('span', class_='text2')
            if color_tag:
                colors.append(color_tag.get_text(strip=True).lower())

        # Ищем элемент с множественными цветами
        multi_color_container = soup.find('ul', class_='color-wrapper radio-group-list', role='radiogroup')
        if multi_color_container:
            color_buttons = multi_color_container.find_all('button', class_='color-attribute')
            for button in color_buttons:
                aria_label = button.get('aria-label', '')
                if 'Select Color' in aria_label:
                    color_name = aria_label.split('Select Color')[-1].strip()
                    colors.append(color_name.lower())

        # Устанавливаем значение массива цветов или None, если цветов нет
        product["color"] = colors if colors else None

        # Устанавливаем значение массива цветов или None, если цветов нет
        # Конвертируем в JSON-string
        product["color"] = json.dumps(colors) if colors else None

        # Извлекаем Style Code
        style_code_tag = soup.find('div', class_='product-detail-id')
        if style_code_tag:
            style_code_text = style_code_tag.get_text(strip=True)
            if "Style Code:" in style_code_text:
                product["style_code"] = style_code_text.split("Style Code:")[-1].strip()
        await asyncio.sleep(3)
        return product  # Successful parse

    except Exception as e:
        print(f"Unexpected error while parsing data: {type(e).__name__},{e}.")
        await asyncio.sleep(1)
        return product