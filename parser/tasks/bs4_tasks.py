import random
import asyncio
import json
import time
import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientResponseError, ServerDisconnectedError
from parser.settings import USER_AGENT


def parse_product_data(page_source):
    """Парсит HTML страницы продукта и извлекает информацию о продукте."""
    soup = BeautifulSoup(page_source, 'lxml')
    # Находим основной контейнер продукта
    product_container = soup.find('div', class_='product-secondary-section pdp-standard')
    print("Found the item container")
    if not product_container:
        print("Product container not found.")
        return None

    # Инициализируем переменные для хранения данных
    product = {
        "name": None,
        "brand_name": None,
        "description": None,
        "original_price_USD": None,
        "discount_price_USD": None,
        "color": None,  # Массив цветов
        "style_code": None
    }

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

    except Exception as e:
        print(f"Error parsing product details: {e}")
    return product


async def async_parse_product_data(session: ClientSession, url: str, proxies: list):
    """Asynchronously parses the HTML of a product page and extracts product information."""
    headers = {
        "User-Agent": USER_AGENT
    }

    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        proxy = f"http://{random.choice(proxies)}"  # Select a random proxy
        try:
            async with session.get(
                    url=url,
                    headers=headers,
                    proxy=proxy,
                    timeout=10
            ) as response:
                # Check if access was denied by status code
                if response.status == 403:
                    print(f"Access denied with proxy {proxy}. Switching proxy...")
                    retry_count += 1
                    time.sleep(3)
                    continue  # Retry with a different proxy

                # Process page content
                page_content = await response.text()
                soup = BeautifulSoup(page_content, 'lxml')

                # Check if the page title is "Access Denied"
                if soup.title and "Access Denied" in soup.title.get_text():
                    print(f"Access denied with proxy {proxy}. Page title is 'Access Denied'. Switching proxy...")
                    retry_count += 1
                    continue  # Retry with a different proxy
                print(f"Got the soup of {url}")
                # Parse product data as usual if no access issues
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

                    return product  # Successful parse
                except Exception as e:
                    print(type(e))


        except ServerDisconnectedError as e:
            print(f"Error: {e}")
            retry_count += 1
            time.sleep(3)

        except ClientResponseError as e:
            print(f"Error with proxy {proxy}: {e}")
            retry_count += 1  # Increment retry count if there's an error
            time.sleep(3)
        except asyncio.TimeoutError:
            print(f"Timeout with proxy {proxy}. Retrying...")
            retry_count += 1
            time.sleep(3)
    print(f"Failed to retrieve data from {url} after {max_retries} attempts.")
    return None




# product = {
    #   "style_code": <div class="product-detail-id">Style Code: 0400021492026</div>
    #    "brand_name":<span class="product-brand-name">
    # <a href="/brand/joe-s-jeans" class="product-brand adobelaunch__brand" data-adobelaunchproductid="0400021910443">Joe's Jeans</a>
    # </span>
    #     "name": <span class="product-name h2">
    # Harris Plaid Bouclé Flannel Shirt</span>,
    #     "description": <div class="value content" id="collapsible-details-1">
    # Joe's Jeans' Harris flannel shirt features a Sedona plaid print and comfortbale bouclé texture. Crafted of soft cotton, the woven design offers both style and comfort.<ul><li>Spread collar</li><li>Long sleeves, barrel cuffs</li><li>Button-front placket</li><li>100% cotton</li><li>Machine wash</li><li>Imported</li></ul><br><b>SIZE &amp; FIT</b><ul><li>Model measurements: 6’2” tall, 40” chest, 31” waist</li><li>Model is wearing a US size Medium</li></ul>
    # <div class="product-detail-id">
    # Style Code: 0400021910443
    # </div>
    # </div>,
    #     "original_price": <span class="formatted_price bfx-price bfx-list-price" content="$189" data-unformatted-price="189" data-bfx="{&quot;original&quot;:[&quot;$189&quot;],&quot;id&quot;:&quot;yzozuibyb&quot;}">
    # &#xFEFF;HKD 1,584.12
    # </span>,
    #     "discount_price": <span class="formatted_sale_price formatted_price js-final-sale-price bfx-price bfx-sale-price" data-unformatted-price="69.99" data-bfx="{&quot;original&quot;:[&quot;$69.99&quot;],&quot;id&quot;:&quot;5a8z34gn0&quot;}">&#xFEFF;HKD 586.63</span>,
    #     "color": container - <ul class="color-wrapper radio-group-list" role="radiogroup">, <ul class="color-wrapper radio-group-list" role="radiogroup"><li role="radio" aria-checked="true">
    # 										<button class="color-attribute radio-group-trigger adobelaunch__colorlink selectable selected" aria-label="Select Color BANDANA" aria-describedby="BANDANA"
# container div class="prices">
# original price <span class="value" content="570.00">
# discount price <span class="value bfx-price" content="299.99">