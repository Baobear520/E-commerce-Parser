# saksoff5th.com parser #

## Task
Scrape data from a list of products (>1000 items) including "style code", "name", "description", "original price", "discount price", "color(s)" and store it in a database.
Ensure that the scraping process is completed within 20 minutes. 
Enable re-scraping functionality (if the same data is retrieved, update only the "last_updated" field in the database.


## Project Description
This project is a web scraping application designed to collect product data from the Saks Off 5th e-commerce website using parallel multi-threading and asynchronous HTTP requests for scraping.
The script also supports the usage of proxies to avoid IP bans and throttling.
It uses Selenium WebDriver to emulate users' actions in Chrome browser and scrape the links to desired products and Beautiful Soup to extract structured product information such as names, prices, descriptions, and other details. 


## Features

1. Automated Browser Control and Data Scraping
 - Use of Selenium WebDriver to emulate users' actions in Chrome browser and scrape the links to desired products
2. Modal Window Handling
 - Detects and closes existing modal windows dynamically to ensure uninterrupted scraping.
3. Dynamic Content Support
 - Uses Selenium WebDriver with headless Chrome to handle JavaScript-heavy pages.
4. Proxy Management:
 - Support for authenticated and unauthenticated proxies.
 - A separate script for reading proxies from a file, validation for correct status code and saving to a file
 - Dynamic proxies rotation mechanism to handle rate limits or IP bans.
5. Parallel Processing:
 - Leverages Python's asyncio and aiohttp for concurrent requests to maximize efficiency and reduce runtime.
 - Utilizes Python's ThreadPoolExecutor to execute multiple scraping tasks simultaneously, increasing speed and efficiency.
6. Retry Logic and Error Handling
 - Robust retry mechanism to handle network errors, access denials, and timeouts.
7. Database Integration
 - Saves scraped data to a SQLite database for easy and fast storage and retrieval
8. Scheduled Rescraping
 - Automatically re-scrapes data at regular intervals.
9. Performance Tracking
 - A runtime counter decorator tracks the execution time of the entire scraping process.


## Installation and Setup

### Requirements:
Python 3.9 or higher.
Google Chrome and the corresponding chromedriver.
Virtual environment (optional but recommended).

### Installation Steps:
Clone the repository:

```
git clone https://github.com/YOUR-USERNAME/UnderTheWeatherPlaylistMaker.git
```
Switch to the project folder:

```
cd UnderTheWeatherPlaylistMaker
```
Set up a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate  # On Windows
```

Install dependencies:

```
pip install -r requirements.txt
```
Set up environment variables for (create a .env file in the project root and add the following lines):
```#Basic settings
TARGET_URL = 'https://www.saksoff5th.com/'
TIMEOUT = #your_value
DELAY = #your_value
MAX_RETRIES = #your_value
MAX_WORKERS = #your_value

#Chrome settings
USER_AGENT = your_value

#Database settings
DB_PATH = name_of_the_db_file

#Proxy testing script
PATH_TO_VALID_PROXIES = name_of_the_file_with_valid_proxies
UPDATE_PROXIES = False
TEST_IP_URL = #any_web_url
```

Set Up ChromeDriver:
Download the version of chromedriver matching your Chrome installation from here.
Ensure chromedriver is in your system's PATH or place it in the project directory.

Configure Proxies:
Add valid proxies 
configurations (if required) to the proxies.txt file or relevant settings.

## Contacts ##

For questions or support, contact via email: admitry424@gmail.com



Написать тестовый парсинг магазина https://www.saksoff5th.com/.

Тестовые задачи:

1) обход защиты от тротлинга - чтобы запросы на сайт не блокировались 
(подсказка - использовать прокси или впн).
Тестовый прокси для экспериментов:
45.130.126.204:8000:tsDLZZ:nsn4Ga

2) Получить список товаров (>1000, название, описание, цена, цвет) 
с длительностью обработки запроса не более 20 минут

3) Записать в любую БД (можно для простоты mongo или даже SQLLite)

4) Сделать возможность рескрапинга, этот же набор товаров получился в аналогичный срок, но изменил дату в базе данных

5) Будет плюсом если это будет обернуто в docker-контейнер

6) Продемонстрировать работу скрипта
