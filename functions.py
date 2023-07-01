from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from re import search

def get_edge_driver(headless:bool=False, user_agent:str=None, cookies:str=None, cache:bool=False):
    options = webdriver.EdgeOptions()

    if headless:
        options.add_argument("headless")

    if user_agent:
        options.add_argument(f"user-agent={user_agent}")

    if cookies:
        options.add_argument(f"user-data-dir={cookies}")

    if cache:
        options.add_argument("cache-control=no-cache")
    
    driver = webdriver.Edge(options=options)

    return driver

def close_donation_dialogs(driver:webdriver.Edge):
    try:
        selector = (By.CLASS_NAME, "spu-close-popup")
        el_list = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(selector))
        
        print('Found %d elements' % len(el_list))

        for el in el_list:
            if el.is_displayed():
                el.click()

    except selenium_exceptions.TimeoutException:
        print('No elements found TimeoutException')
        pass

    except selenium_exceptions.NoSuchElementException:
        print('No elements found NoSuchElementException')
        pass

def close_notification_dialog(driver:webdriver.Edge):
    try:
        selector = (By.ID, "onesignal-slidedown-cancel-button")
        el = WebDriverWait(driver, 5).until(EC.presence_of_element_located(selector))

        print('Found element')

        if el.is_displayed():
            el.click()

    except selenium_exceptions.TimeoutException:
        print('No elements found TimeoutException')
        pass

    except selenium_exceptions.NoSuchElementException:
        print('No elements found NoSuchElementException')
        pass

def close_dialogs(driver:webdriver.Edge):
    close_notification_dialog(driver)
    close_donation_dialogs(driver)

def get_chapter_element_urls(el):
    urls = []

    try:
        links = el.find_elements(By.TAG_NAME, 'a')
        urls = [link.get_attribute('href') for link in links]

    except selenium_exceptions.NoSuchElementException:
        print('No links found')

    except selenium_exceptions.StaleElementReferenceException:
        print('Stale element')

    return urls

def get_chapter_url_list(driver:webdriver.Edge):
    el_list = driver.find_elements(By.CLASS_NAME, "su-spoiler")

    elements = {}

    for el in el_list:
        if el.is_displayed() is False:
            continue

        urls = get_chapter_element_urls(el)

        try:
            title = el.find_element(By.CLASS_NAME, 'su-spoiler-title')
        except selenium_exceptions.NoSuchElementException:
            print('No title found')
            continue

        # regex number
        match = search(r'\d+', title.text)

        if match is None:
            key = title.text
        else:
            key = match.group()

        elements[key] = urls
        
    return elements

def get_chapter_url(driver, n_chapter:int):
    el_list = driver.find_elements(By.CLASS_NAME, "su-spoiler")

    for el in el_list:
        if el.is_displayed() is False:
            continue

        try:
            title = el.find_element(By.CLASS_NAME, 'su-spoiler-title')
        except selenium_exceptions.NoSuchElementException:
            print('No title found')
            continue

        # regex number
        match = search(r'\d+', title.text)

        if match is None:
            continue

        n = int(match.group())
        
        if n != n_chapter:
            continue

        return get_chapter_element_urls(el)
    
    return None