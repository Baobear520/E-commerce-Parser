import requests

def get_html(url):
    proxy = {
        'http': 'http://tsDLZZ:nsn4Ga@45.130.126.204:8000',
        'https': 'http://tsDLZZ:nsn4Ga@45.130.126.204:8000'
    }
    response = requests.get(url, proxies=proxy)
    return response.html

def get_page_hash(content):
    # Создаем хэш от HTML содержимого
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def save_page_content(content):
    page_hash = get_page_hash(content)
    # Сохранение в базу данных: url, page_hash
    cache.update({"page": page_hash})


def parse_html(source):
    data = ""
    return data

def save_to_db(data,db):
    pass

def check_or_update_cache(content):
    page_hash = cache.get("page")
    if not page_hash:
        or page_hash != get_page_hash(content):




def main(url,db):
    if not check_or_update_cache(html):
        html = get_html(url)
        save_page_content(html)
        data = parse_html(html)
    save_to_db(data,db)


if __name__ == "__main__":
    url = "https://www.saksoff5th.com/"
    db = {}
    main(url,db)

