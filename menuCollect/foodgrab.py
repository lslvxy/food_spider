import json
import logging
import os
import re
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

log = []
bc = logging.basicConfig(level=logging.INFO, format='%(asctime)s  - %(message)s')


def fetch_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    i = 0
    while i < 10:
        if response.status_code == 200:
            log.append("Request to page, data being pulled")
            logging.info("Request to page, data being pulled")
            break
        i += 1
        log.append("Page response failed, retrying")
        logging.info("Page response failed, retrying")
        time.sleep(5)
        response = requests.request("GET", url, headers=headers, data=payload)
    if i == 10 and response.status_code != 200:
        log.append("Page response failed, please check network link and try again later")
        logging.info("Page response failed, please check network link and try again later")
        return log
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def find_by_name(categories, name):
    for c in categories:
        if c.get('name') == name:
            return c


def fetch_restaurant(page_url):
    soup = fetch_soup(page_url)
    if soup is None:
        return None, None

    category_soup = soup.find_all("script", class_="next-head")
    i = 0
    while i < 10:
        if category_soup:
            log.append("Data has been pulled and is being parsed")
            logging.info("Data has been pulled and is being parsed")
            break
        i += 1
        log.append("No data pulled, retrying")
        logging.info("No data pulled, retrying")
        time.sleep(5)
        soup = fetch_soup(page_url)
        category_soup = soup.find_all("script", class_="next-head")
    if i == 10 and category_soup == []:
        log.append("Failed to pull data, please check network link and try again later")
        logging.info("Failed to pull data, please check network link and try again later")
        return log

    data = {}
    for category in category_soup:
        cat_json = json.loads(category.get_text())
        if cat_json['@type'] == 'Restaurant':
            data = cat_json
            break
    return data, soup


def fetch_config_data(soup, variables):
    next_data = json.loads(soup.find("script", id="__NEXT_DATA__").get_text())
    product_options_list = next_data.get('props').get('initialReduxState').get('pageRestaurantDetail').get(
        'entities').get(variables['id']).get('menu').get('categories')
    return product_options_list



# def output_image():

def parse_foodgrab(page_url, variables):
    restaurant_data, soup = fetch_restaurant(page_url)
    if restaurant_data is None:
        return None
    product_options_list = fetch_config_data(soup, variables)

    # print(menu_categories)
    tab_categories = restaurant_data.get('hasMenu').get('hasMenuSection')
    food_grab_list = []
    for category in tab_categories:
        category_name = re.sub(r'[:/\\?*“”<>|""]', '_', category.get('name'))
        product_option = find_by_name(product_options_list, category_name)
        products = category.get('hasMenuItem')
        for product in products:
            out = {}
            product_name = product.get('name')
            item_name = re.sub(r'[:/\\?*“”<>|""]', '_', product_name)
            # out.clear()
            total_category = category_name
            store_name = page_url.split('/')[-1]
            if not os.path.exists(f"..\\Aim_menu\\food_grab\\{store_name}\\{category_name}"):
                os.makedirs(f"..\\Aim_menu\\food_grab\\{store_name}\\{category_name}")
            total_item_name = item_name
            total_description = product.get('description')
            total_item_price = product.get('offers').get('price')
            # out['币种'] = str(product.get('offers').get('priceCurrency'))
            food_grab_list.append(out)
            if product_option != None:
                product_item = find_by_name(product_option['items'], product_name)
                total_item_image = product_item.get('images')
                if total_item_image != []:
                    item_image = product_item.get('images')[0]
                    r = requests.get(item_image, timeout=180)
                    with open(f"..\\Aim_menu\\food_grab\\{store_name}\\{category_name}\\{item_name}.jpg", 'wb') as f:
                        f.write(r.content)
                modifier_groups = product_item.get('modifierGroups')
                for modifier_group in modifier_groups:
                    total_modifier_group = modifier_group.get('name')
                    total_select_type = 'Single choice' if modifier_group.get('selectionType') == 0 else 'multiple choice'
                    total_required_or_not = modifier_group.get('selectionRangeMin') == modifier_group.get(
                        'selectionRangeMax') == 1
                    total_min_available = modifier_group.get('selectionRangeMin')
                    total_max_available = modifier_group.get('selectionRangeMax')
                    modifier_items = modifier_group.get('modifiers')
                    for modifier_item in modifier_items:
                        total_options = modifier_item.get('name')
                        total_options_price = (modifier_item.get('priceInMinorUnit')/100)
                        out = {}
                        out['category'] = total_category
                        out['item_name'] = total_item_name
                        out['description'] = total_description
                        out['item_price'] = total_item_price
                        out['modifier_group'] = total_modifier_group
                        out['select_type'] = total_select_type
                        out['required_or_not'] = total_required_or_not
                        out['min_available'] = total_min_available
                        out['max_available'] = total_max_available
                        out['options'] = total_options
                        out['options_price'] = total_options_price
                        food_grab_list.append(out)
            out = {}
            out['category'] = total_category
            out['item_name'] = total_item_name
            out['description'] = total_description
            out['item_price'] = total_item_price
            # out['modifier_group'] = total_modifier_group
            # out['select_type'] = total_select_type
            # out['required_or_not'] = total_required_or_not
            # out['min_available'] = total_min_available
            # out['max_available'] = total_max_available
            # out['options'] = total_options
            # out['options_price'] = total_options_price
            food_grab_list.append(out)
    food_grab_excel_list = []
    i = 0
    while i < len(food_grab_list):
        excel_category_name = (food_grab_list[i]).get('category')
        excel_item_name = (food_grab_list[i]).get('item_name')
        excel_description = (food_grab_list[i]).get('description')
        excel_item_price = (food_grab_list[i]).get('item_price')
        excel_modifier_group = (food_grab_list[i]).get('modifier_group')
        excel_select_type = (food_grab_list[i]).get('select_type')
        excel_required_or_not = (food_grab_list[i]).get('required_or_not')
        excel_min_available = (food_grab_list[i]).get('min_available')
        excel_max_available = (food_grab_list[i]).get('max_available')
        excel_options = (food_grab_list[i]).get('options')
        excel_options_price = (food_grab_list[i]).get('options_price')
        food_grab_excel_list.append([excel_category_name, excel_item_name, excel_description, excel_item_price, excel_modifier_group, excel_select_type, excel_required_or_not, excel_min_available, excel_max_available, excel_options, excel_options_price])
        i += 1
    df = pd.DataFrame(food_grab_excel_list, columns=["category_name", "item_name", "description", "item_price", "modifier_group","select_type", "required_or_not", "min_available", "max_available", "options", "options_price"])
    if os.path.exists(f"..\\Aim_menu\\food_grab\\{store_name}.xlsx"):
    	os.remove(f"..\\Aim_menu\\food_grab\\{store_name}.xlsx")
    df.to_excel(f"..\\Aim_menu\\food_grab\\{store_name}.xlsx", index=False)
    log.append("Collection complete")
    logging.info("Collection complete")
    return log








# if __name__ == '__main__':
#     url = 'https://food.grab.com/sg/en/restaurant/saap-saap-thai-jewel-changi-airport-b1-299-delivery/4-CZKELFETJBEBG6'
#     id = url.split('/')[-1]
#     parse_foodgrab(id, url)
