from bs4 import BeautifulSoup


def parse_product_data(page_source):

    soup = BeautifulSoup(page_source, 'lxml')

    product_container = soup.find('div', class_='product-secondary-section pdp-standard')
    print("Found the item container")
    if not product_container:
        print("Product container not found.")
        return None

    # product = {
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
    #     "color": <span class="attr-name adobelaunch__colorlink" data-adobelaunchcolorproductid="0400021910443" data-adobelaunchproductcolor="BLACK MULTI"><span class="text1">Color: </span><span class="text2">BLACK MULTI</span></span>
    # }


    # Инициализируем переменные для хранения данных
    product = {
        "name": None,
        "brand_name": None,
        "description": None,
        "original_price": None,
        "discount_price": None,
        "color": None
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
            # Берем только первый абзац описания, игнорируя списки и другую информацию
            description = description_tag.get_text(strip=True).split(".")[0] + "."
            product["description"] = description

        # Извлекаем оригинальную цену (без скидки)
        original_price_tag = soup.find('span', class_='formatted_price bfx-price bfx-list-price')
        if original_price_tag and original_price_tag.has_attr('content'):
            product["original_price"] = float(original_price_tag['content'].replace('$', '').replace(',', ''))

        # Извлекаем цену со скидкой
        discount_price_tag = soup.find('span',
                                       class_='formatted_sale_price formatted_price js-final-sale-price bfx-price bfx-sale-price')
        if discount_price_tag and discount_price_tag.has_attr('content'):
            product["discount_price"] = float(discount_price_tag['content'].replace('$', '').replace(',', ''))
        else:
            # Если скидочная цена не найдена, используем оригинальную цену
            product["discount_price"] = None

        # Извлекаем цвет
        color_tag = soup.find('span', class_='attr-name adobelaunch__colorlink')
        if color_tag:
            color_name_tag = color_tag.find('span', class_='text2')
            product["color"] = color_name_tag.get_text(strip=True).lower() if color_name_tag else "Color not specified"

    except Exception as e:
        print(f"Error parsing product details: {e}")
    return product


