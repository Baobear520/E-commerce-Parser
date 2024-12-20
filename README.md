# Saksoff5th.com Data Scraper #

## Task
- Scrape data from a list of >1000 products (used [saksoff5th.com/c/men](https://www.saksoff5th.com/c/men) as a default) including fields such as "style code", "name", "description", "original price", "discount price", "color(s)" and store the data in a database.
- Ensure that the scraping process is completed within 20 minutes. 
- Enable re-scraping functionality (if the same data is retrieved, update only the "last_updated" field in the database.

## Project Description
This project is a web scraping application designed to extract and store product data from [saksoff5th.com](https://www.saksoff5th.com) using parallel multi-threading and asynchronous HTTP requests for scraping.

## Features

#### Automated Browser Control and Data Scraping

 Use of Selenium WebDriver to emulate users' actions in Chrome browser and scrape the links to desired products

#### 2. Modal Window Handling

 Detects and closes existing modal windows dynamically to ensure uninterrupted scraping.

#### 3. Dynamic Content Support

 Uses Selenium WebDriver with headless Chrome to handle JavaScript-heavy pages.
#### 4. Proxy Management:
 - Support for authenticated and unauthenticated proxies.
 - A separate script for reading proxies from a file, validation for correct status code and saving to a file
 - Dynamic proxies rotation mechanism to handle rate limits or IP bans.

#### 5. Parallel Processing:
 - Leverages Python's asyncio and aiohttp for concurrent requests to maximize efficiency and reduce runtime.
 - Utilizes Python's ThreadPoolExecutor to execute multiple scraping tasks simultaneously, increasing speed and efficiency.
#### 6. Retry Logic and Error Handling
 Robust retry mechanism to handle network errors, access denials, and timeouts.
#### 7. Database Integration
 Saves scraped data to a SQLite database for easy and fast storage and retrieval
#### 8. Scheduled Rescraping
 Automatic pipeline for re-scraping data at regular intervals.
#### 9. Performance Tracking
 A runtime counter decorator tracks the execution time of the entire scraping process.


## Installation and Setup

### Requirements:
Python 3.9+
SQLite database
Google Chrome and the corresponding chromedriver.


### Installation Steps:
Clone the repository:

```
git clone https://github.com/Baobear520/Saksoff5th.com_data_scraper.git
```
Switch to the project folder:

```
cd Saksoff5th.com_data_scraper
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
Set up environment variables for the project(create a .env file in the project root and add the following lines):
```
#Basic settings
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

### Set Up ChromeDriver:
Download the version of chromedriver matching your Chrome installation from here.
Ensure chromedriver is in your system's PATH or place it in the project directory.

### Configure Proxies:

Configuration comes down to having a list of valid proxies in the designated file ```valid_proxies.txt``` from which the main script reads proxies.

To simplify validation of available proxies, I wrote a separate script that reads proxies from the file, asynchronously makes HTTP requests to a mock URL (set in the TEST_IP_URL variable) for proxy address validation and then saves valid proxies to ```data/valid_proxies.txt```.  
### Testing available proxies

I recommend you first create a "data" folder in the root directory for keeping all non-parsing related files or data.

 - create a file "anon_proxies.txt" in the data folder if your proxies don't require authentication. Elsewise, name the file "auth_proxies.txt"
 - add your list of proxies to the file
 - the main coroutine that runs proxy testing script is ```check_proxies``` located at ```other_scripts/proxy_testing/test_proxies.py```.
It has one required positional argument ```has_proxy_auth``` which is by default set to ```False```. Change it to ```True``` if your proxies require authentication.
 - execute the testing script:
   ```
   python other_scripts/proxy_testing/test_proxies.py
   ```
## Running the script
There are two independent scripts that use different approaches:
### using_threads.py
**The script uses Selenium WebDriver and multithreading to scrape product data from a website (Saksoff5th) and save it to a SQLite database.**

The whole scraping process is controlled by ```scheduler```  - function that runs the scraper in a given intervals of time (in our case the main scraping logic is locked within ```main`` function of the file).

The script in ```main``` function initializes a database and sets up a WebDriver instance (```connect_to_base_url``` function) with optional proxy usage. If proxies are used, the script starts an event loop to read them asynchronously from ''valid_proxies.txt```.

Next, it navigates to the target URL and selects **Men** from a dropdown menu where the target products are located. The function ```select_section_from_dropdown_menu``` contains logic for handling pop-up modal windows that can intercept clicking on the dropdown menu section.
and locates pagination elements.

Then, the script enters the main scraping loop, where it:
 - scrolls down the current page to generate HTML of all the product objects (```locate_pagination``` function)
 - scrapes product URLs from the current page using Selenium.
 - puts the URLs into a queue.
 - uses a ThreadPoolExecutor to parallelize the scraping process, with each worker task creating a separate WebDriver instance to scrape product data from the URLs in the queue, saving the results in the database and appending it to the list of all the products (```all_products```).
> Before creating a pool of threads for product URLs, the main webdriver navigates to the next page and awaits until the queue of product URLs from the previous page is empty
e.g. scraping of the product data is done.

The script repeats the scraping loop until it has scraped 1000 products.
Finally, the script quits the WebDriver instance and prints a summary of the scraped products.


## Contacts ##

admitry424@gmail.com
