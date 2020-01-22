import urllib.request
import urllib.parse
from urllib.parse import unquote
import os
import sys
from lxml.etree import fromstring
from lxml import html
import sys
from pymongo import MongoClient
from collections.abc import Iterable
import warnings
from bs4 import BeautifulSoup
import re
import requests
import logging
import threading
import time
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
# from pyvirtualdisplay import Display


def unique(data):
    return list(dict.fromkeys(data))


# Edit the following variables
client = MongoClient()
DB_NAME = 'elmenus'
db = client[DB_NAME]
elmenus_collection = db['data']


def get_driver():
    """
    This function returns the selenium web driver object.
    
    Parameters:
        None
    
    Returns:
        driver: selenium web driver object
    """
    options = webdriver.FirefoxOptions()
    # options.add_argument('-headless')

    driver = webdriver.Firefox(executable_path='D:\DataScience\Projects\INetworks\skilldna\scrappers\geckodriver.exe', firefox_options = options)

    return driver


def get_soup(url):
    """
    Given the url of a page, this function returns the soup object.
    
    Parameters:
        url: the link to get soup object for
    
    Returns:
        soup: soup object
    """
    driver = get_driver()

    driver.get(url)
    driver.implicitly_wait(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    driver.close()

    return soup


#save to database
def saveToDB(collection, city_areas_zones_dict): 
    try:
        print("New record will be inserted!")
        collection.insert(city_areas_zones_dict, check_keys=False)
        return True
    except Exception as e:
        print('Exception : %s' % str(e))
    

def main():
    base_url = 'https://www.elmenus.com'
    # uniqueJobs = requests.get(base_url).json()
    home_page_soup = get_soup(base_url)
    dropdown_menu_ul = home_page_soup.find("ul",{"class":"dropdown-menu inner"})
    cities_names = []
    for li in dropdown_menu_ul:
        cities_names.append(li.text.strip())
    print("Number of Cities: ", len(cities_names))
    print("Cities: ", cities_names)
    cities_num = len(cities_names)

    driver = get_driver()
    base_url = "https://www.elmenus.com/cairo/delivery"
    driver.get(base_url)
    header_div = driver.find_element_by_class_name('area-zone-content')
    header_div_soup = header_div.get_attribute('innerHTML')
    # cities_list_ul =  driver.find_elements_by_class_name("zone-btn")
    # cities_names = [ city.text.strip() for city in cities_list_ul]

    city_areas_zones_dict = {}

    for city_index,city_name in enumerate(cities_names):
        print("Current City Name: ", city_name)

        city_css_selector = '#cities-list > li:nth-child('+ str(city_index+1) +') > button'
        # print("city_css_selector: ", city_css_selector)
        city_button = driver.find_elements_by_css_selector(city_css_selector)
        city_button = city_button[0]
        driver.execute_script("arguments[0].click();",city_button)
        driver.implicitly_wait(3)

        areas_list_buttons =  driver.find_elements_by_class_name("area-btn")
        areas_names = [ area.text.replace("AS","").strip() for area in areas_list_buttons]
        areas_names = [area for area in areas_names if area != '']
        areas_num = len(areas_names)
        print("Areas: ", areas_names)
	
        areas_zones_dict = {}
        for area_index in range(1, areas_num + 1 ):
            area = areas_list_buttons[area_index-1] 
            area_name = areas_names[area_index-1]
            print(">>> Current Area Name: ", area_name)
	
            area_button = areas_list_buttons[area_index-1]
            # area_button.click()
            driver.execute_script("arguments[0].click();",area_button)
            driver.implicitly_wait(3)
            time.sleep(1)

            zones_list =  driver.find_elements_by_class_name("city-area-zone")
            zones_names = [ zone.text.strip() for zone in zones_list]
            zones_names = [zone for zone in zones_names if zone != '']
            print(">>>>>> zones_names: ", zones_names)
            areas_zones_dict[area_name] = zones_names
        city_areas_zones_dict[city_name] = areas_zones_dict
        time.sleep(3)
        print("----------------------------------")
        
    print("city_areas_zones_dict: ", city_areas_zones_dict)
    saveToDB(elmenus_collection, city_areas_zones_dict)

import json
def generate_csv_file():
    json_file_path = 'D:\DataScience\Projects\INetworks\Hive\elmenus_data.json'
    cities = []
    areas = []
    zones = []
    for line in open(json_file_path, encoding='utf-8'):
        dict = json.loads(line) 
        # print(dict)
        del dict['_id']
        for city, areas_dict in dict.items():
            # print(">>> ", city)
            for area, zones_list in areas_dict.items():
                # print(area, zones)
                for zone in zones_list:
                    print(city, area, zone)
                    cities.append(city)
                    areas.append(area)
                    zones.append(zone)
            print("----------------------------------")

    df = pd.DataFrame({'City':cities,'Area':areas,'Zone':zones})   # pd.read_json()
    print(df.head())
    df.to_csv('elmenus_data.csv')

if __name__ =='__main__':
    # main()
    generate_csv_file()


