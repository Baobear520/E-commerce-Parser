import json
import os
import zipfile

def save_to_json(data,file_name):
    base_path = "data/json_files/"
    os.makedirs(base_path, exist_ok=True)
    path_to_file = base_path + file_name

    with open(path_to_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Saved successfully!")


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