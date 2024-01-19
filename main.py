from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from tabulate import tabulate
import textwrap
import json
import traceback
import os
# Get the current working directory
current_directory = os.getcwd()

chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory': current_directory+'/assets'}
chrome_options.add_experimental_option('prefs', prefs)

# Instantiate a Chrome browser with the configured options
driver = webdriver.Chrome(options=chrome_options)

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
    page_limit = 97
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

def download_data():
    #load json data
    data = {}
    with open('data.json') as json_file:
        data = json.load(json_file)

    #load login info from config.json
    login_info = {}
    with open('config.json') as json_file:
        login_info = json.load(json_file)
    
    #login
    driver.get('https://craftpix.net/my-account/')

    #add username email
    username_input = driver.find_element(By.ID, 'username')
    username_input.send_keys(login_info['username'])

    #add password
    password_input = driver.find_element(By.ID, 'password')
    password_input.send_keys(login_info['password'])


    #login button
    login_button = driver.find_element(By.NAME, 'login')
    login_button.click()

    #wait for login
    driver.implicitly_wait(10)

    test = False
    if test:
        #go to first page
        driver.get(data['1'][0]['Link'])
        #wait for page to load
        driver.implicitly_wait(2)
        #download button
        download_button = driver.find_element(By.XPATH, '//*[@id="commerce_unit"]/div/a')

        #get href
        href = download_button.get_attribute('href')
        driver.get(href)
        
    
        #wait for terminal input
        input("Press enter to continue...")
        exit()

    #for each page in data get the links and go to the page
    for page in data:
        print("Downloading page:", page)

        for item in data[page]:
            print("Downloading item:", item['Title'])
            driver.get(item['Link'])
            #wait for page to load
            driver.implicitly_wait(2)
            #download button
            download_button = driver.find_element(By.XPATH, '//*[@id="commerce_unit"]/div/a')

            #get href
            href = download_button.get_attribute('href')
            driver.get(href)
            driver.implicitly_wait(5)
            
            

            




    pass

def collect_data_andcompare():
    url = 'https://craftpix.net/all-game-assets/'
    driver.get(url)

    wait_for_element(driver, By.XPATH, '//*[@id="wrap"]/section/main')

    page_num = 1
    page_limit = 98
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

            traceback.print_exc()

            print("An error occurred during navigation or data extraction.")
            break
        page_num += 1
        if page_num > page_limit:
            print("Page limit reached.")
            break
    


    driver.quit()

    # Save data to a json file with 4 spaces indentation
    with open('tocompare.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

    #compare data.json and tocompare.json
    #load json data
    data = []
    with open('data.json') as json_file:
        tmp = json.load(json_file)
        
        for page in tmp:
            for item in tmp[page]:
                data.append(item)
        

        
    to_compare = []
    with open('tocompare.json') as json_file:
        tmp = json.load(json_file)
        for page in tmp:
            for item in tmp[page]:
                to_compare.append(item)

    
    missing = {}
    #compare data and to_compare links
    for item in to_compare:
        found = False
        for item2 in data:
            if item['Link'] == item2['Link']:
                found = True
                break
        if not found:
            print("Not found:", item['Link'])
            print("Title:", item['Title'])
            print("Category:", item['Category'])
            print("Price:", item['Price'])
            print("Link:", item['Link'])
            print("")
            #create missing.json similar to data.json but have number 1 only with the missing links
            missing["1"] = item
           
            

                

        
        if found:
            print("Found:", item['Link'])
            print("Title:", item['Title'])
            print("Category:", item['Category'])
            print("Price:", item['Price'])
            print("Link:", item['Link'])
            print("")

    with open('missing.json', 'w') as outfile:
                json.dump(missing, outfile, indent=4)
    
    print("missing links added to missing.json")

            

                    
    pass

if __name__ == "__main__":
    #collect_data()
    
    #download_data()

    #collect_data and compare to data.json
    collect_data_andcompare ()


    exit()


