from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from tabulate import tabulate
import textwrap
import json

driver = webdriver.Chrome()

def truncate_text(text, max_length=30):
    return textwrap.shorten(text, width=max_length, placeholder="...")

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def extract_data_from_page(page_element):
    articles = page_element.find_elements(by=By.TAG_NAME, value='article')
    data = []
    for article in articles:
        title = article.find_element(by=By.TAG_NAME, value='h2').text
        category_element = article.find_element(by=By.TAG_NAME, value='a')
        category = category_element.text if category_element.text.strip() else "No category"
        link_element = article.find_element(by=By.TAG_NAME, value='a')
        link = link_element.get_attribute('href')

        try:
            price = article.find_element(by=By.TAG_NAME, value='bdi').text
        except NoSuchElementException:
            pricediv = article.find_element(by=By.TAG_NAME, value='div')
            if pricediv.get_attribute("class") == "premium icon":
                price = "membership"
            else:
                price = "free"

        data.append({
            'Title': truncate_text(title),
            'Category': category,
            'Price': price,
            'Link': link
        })
    #convert data to list to tabulate
    tabulate_data = []
    for item in data:
        tabulate_data.append(list(item.values()))
        
    print(tabulate(tabulate_data, headers=['Title', 'Category', 'Price', 'Link']))
    return data

def collect_data():
    url = 'https://craftpix.net/all-game-assets/'
    driver.get(url)

    wait_for_element(driver, By.XPATH, '//*[@id="wrap"]/section/main')

    page_num = 1
    page_limit = 4
    data = {}  # Initialize data here
    while True:
        try:
            
            next_page_url = f'{url}page/{page_num}/'
            print("Navigated to the next page:", next_page_url)
            driver.get(next_page_url)

            wait_for_element(driver, By.XPATH, '//*[@id="wrap"]/section/main')

            print("Navigated to the next page.")

            main_section = driver.find_element(by=By.XPATH, value='//*[@id="wrap"]/section/main')
            data[page_num] =  extract_data_from_page(main_section)

            print("Data extracted from the current page.")
        except NoSuchElementException:
            print("No more pages.")
            break
        except Exception as e:
            print(f"Exception: {str(e)}")
            #print stack trace
            import traceback
            traceback.print_exc()

            print("An error occurred during navigation or data extraction.")
            break
        page_num += 1
        if page_num > page_limit:
            print("Page limit reached.")
            break
    


    driver.quit()

    # Save data to a json file with 4 spaces indentation
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

if __name__ == "__main__":
    collect_data()
    # Exit after collecting data to prevent the following code from running
    exit()


