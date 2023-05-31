import json
import logging
import time
import os
import re
import requests
import pandas as pd

log = []
bc = logging.basicConfig(level=logging.INFO, format='%(asctime)s  - %(message)s')


def fetch_json(page_url, variables):
    api_url = 'https://%s.fd-api.com/api/v5/vendors/%s?include=menus,bundles,multiple_discounts&language_id=6&basket_currency=TWD&show_pro_deals=true'
    complete_url = api_url % (variables['country'], variables['id'])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    payload = {}
    response = requests.request("GET", complete_url, headers=headers, data=payload)
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
        response = requests.request("GET", complete_url, headers=headers, data=payload)
    if i == 10 and response.status_code != 200:
        log.append("Page response failed, please check network link and try again later")
        logging.info("Page response failed, please check network link and try again later")
        return None
    return response.json()


def parse_foodpanda(page_url, variables):
    product_info = fetch_json(page_url, variables)
    root_data = product_info.get('data', None)

    if root_data is None:
        log.append("Failure to parse menu data")
        logging.info("Failure to parse menu data")
        return
    menus = root_data.get('menus', None)
    if menus is None:
        log.append("Failure to parse menu data")
        logging.info("Failure to parse menu data")
        return

    menu_categories = menus[0].get('menu_categories')

    if menu_categories is None:
        log.append("Failure to parse menu category data")
        logging.info("Failure to parse menu category data")
        return
    # return log

    toppings = root_data.get('toppings')

    # print(toppings)
    food_panda_list = []
    store_name = menus[0].get('name')
    for category in menu_categories:
        products_list = category.get('products', None)
        full_category_name = category['name']
        category_name = re.sub(r'[:/\\?*“”<>|""]', '_',full_category_name)
        if not os.path.exists(f"..\\Aim_menu\\food_panda\\{store_name}\\{category_name}"):
            os.makedirs(f"..\\Aim_menu\\food_panda\\{store_name}\\{category_name}")
        if products_list is None:
            logging.info("category：{name}，no information".format(name=category['name']))
            continue
        for product in products_list:
            # result = {}
            # result.clear()
            item_name = re.sub(r'[:/\\?*“”<>|""]', '_', product.get('name'))
            total_category = category_name
            total_item_name = item_name
            total_description = product.get('description')
            product_variations = product.get('product_variations')
            total_image = '' if product['images'] == [] else product['images'][0]['image_url']
            if total_image != '':
                item_image = total_image
                r = requests.get(item_image, timeout=180)
                with open(f"..\\Aim_menu\\food_panda\\{store_name}\\{category_name}\\{item_name}.jpg", 'wb') as f:
                    f.write(r.content)
            if product_variations is None:
                log.append("product ：{name}，no information".format(name=product.get('name')))
                logging.info("product ：{name}，no information".format(name=product.get('name')))
                continue
            for pv in product_variations:
                total_package_type = pv.get('name', '默认')
                total_package_price = pv.get('price')
                topping_ids = pv['topping_ids']
                if topping_ids:
                    for id in topping_ids:
                        topping = toppings.get(str(id))
                        total_modifier_group = topping.get('name')
                        total_select_type = '单选' if topping.get('quantity_maximum') == 1 else '多选'
                        total_required_or_not = topping.get('quantity_minimum') == topping.get('quantity_maximum') == 1
                        total_min_available = topping.get('quantity_minimum')
                        total_max_available= topping.get('quantity_maximum')
                        options = topping['options']
                        for op in options:
                            total_options = op.get('name')
                            total_options_price = op.get('price')
                            result={}
                            result['category'] = total_category
                            result['item_name'] = total_item_name
                            result['description'] = total_description
                            result['package_type'] = total_package_type
                            result['package_price'] = total_package_price
                            result['modifier_group'] = total_modifier_group
                            result['select_type'] = total_select_type
                            result['required_or_not'] = total_required_or_not
                            result['min_available'] = total_min_available
                            result['max_available'] = total_max_available
                            result['options'] = total_options
                            result['options_price'] = total_options_price
                            food_panda_list.append(result)
            result = {}
            result['category'] = total_category
            result['item_name'] = total_item_name
            result['description'] = total_description
            result['package_type'] = total_package_type
            result['package_price'] = total_package_price
            # result['modifier_group'] = total_modifier_group
            # result['select_type'] = total_select_type
            # result['required_or_not'] = total_required_or_not
            # result['min_available'] = total_min_available
            # result['max_available'] = total_max_available
            # result['options'] = total_options
            # result['options_price'] = total_options_price
            food_panda_list.append(result)
    food_panda_excel_list = []
    i = 0
    while i < len(food_panda_list):
        excel_category_name = (food_panda_list[i]).get('category')
        excel_item_name = (food_panda_list[i]).get('item_name')
        excel_description = (food_panda_list[i]).get('description')
        excel_package_type = (food_panda_list[i]).get('package_type')
        excel_package_price = (food_panda_list[i]).get('package_price')
        excel_modifier_group = (food_panda_list[i]).get('modifier_group')
        excel_select_type = (food_panda_list[i]).get('select_type')
        excel_required_or_not = (food_panda_list[i]).get('required_or_not')
        excel_min_available = (food_panda_list[i]).get('min_available')
        excel_max_available = (food_panda_list[i]).get('max_available')
        excel_options = (food_panda_list[i]).get('options')
        excel_options_price = (food_panda_list[i]).get('options_price')
        food_panda_excel_list.append(
            [excel_category_name, excel_item_name, excel_description, excel_package_type, excel_package_price, excel_modifier_group,
             excel_select_type, excel_required_or_not, excel_min_available, excel_max_available, excel_options,
             excel_options_price])
        i += 1
    df = pd.DataFrame(food_panda_excel_list,
                      columns=["category_name", "item_name", "description", "package_type", "package_price", "modifier_group",
                               "select_type", "required_or_not", "min_available", "max_available", "options",
                               "options_price"])
    if os.path.exists(f"..\\Aim_menu\\food_panda\\{store_name}.xlsx"):
        os.remove(f"..\\Aim_menu\\food_panda\\{store_name}.xlsx")
    df.to_excel(f"..\\Aim_menu\\food_panda\\{store_name}.xlsx", index=False)
    log.append("Collection complete")
    logging.info("Collection complete")
    return log




# if __name__ == '__main__':
#     test_url = 'https://www.foodpanda.hk/restaurant/v3iw/bakeout-homemade-koppepan'
#     parse_foodpanda(test_url)
