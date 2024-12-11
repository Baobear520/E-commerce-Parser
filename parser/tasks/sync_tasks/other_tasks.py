import asyncio
import json
import os
import random
import threading
import time
import zipfile

from parser.settings import PATH_TO_VALID_PROXIES, USER_AGENT
from other_scripts.test_proxies import check_proxies
from parser.tasks.async_tasks.other_async_tasks import async_get_proxies


def save_to_json(data,file_name):
    base_path = "data/json_files/"
    os.makedirs(base_path, exist_ok=True)
    path_to_file = base_path + file_name

    with open(path_to_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Saved successfully to {path_to_file}!")


def save_to_zip(manifest_json, background_js, file_name):
    """Создает ZIP-архив для расширения Chrome с файлами manifest.json и background.js."""
    base_path = "data/"
    os.makedirs(base_path, exist_ok=True)  # Создаем директорию, если она не существует
    path_to_file = base_path + file_name

    with zipfile.ZipFile(path_to_file, 'w') as zp:
        zp.writestr('manifest.json', manifest_json)  # Записываем manifest.json
        zp.writestr('background.js', background_js)  # Записываем background.js

    return path_to_file


def save_to_html(page_source,file_name):
    base_path = "data/html_files/"
    os.makedirs(base_path, exist_ok=True)  # Создаем директорию, если она не существует
    path_to_file = base_path + file_name
    with open(path_to_file, 'w') as file:
        file.write(page_source)
    print(f"Page saved as {path_to_file}")


# def save_to_db(products, db_name="products_db", collection_name="men_products"):
#     """Сохраняет данные о продуктах в базу MongoDB."""
#     client = MongoClient('mongodb://localhost:27017/')
#     db = client[db_name]
#     collection = db[collection_name]
#     collection.create_index("product_id", unique=True)
#
#     # Вставляем данные сразу все товары с текущей страницы
#     if isinstance(products, list) and products:
#         collection.insert_many(products)
#         print(f"Inserted {len(products)} products into MongoDB.")
#     else:
#         print("No products to insert.")
#
#     client.close()

def get_proxies(source,require_proxy_auth,update_proxy_source=False):
    try:
        if update_proxy_source:
            asyncio.run(check_proxies(has_proxy_auth=require_proxy_auth))
    except Exception as e:
        print(f"An error occurred during proxy source updating: {type(e).__name__}, {e}")

    try:
        with open(source,"r") as f:
            return [p for p in f]
    except Exception as e:
        print(f"Error while opening the file: {type(e).__name__},{e}")









if __name__ == "__main__":
    asyncio.run(async_get_proxies(PATH_TO_VALID_PROXIES))