import json
import logging
import time
import os
import re
import requests
import pandas as pd

from menuCollect.url_parse import isEn
from menuCollect.url_parse import isCn

from menuCollect.url_parse import isTh

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
        category_name = re.sub(r'[:/\\?*“”<>|""]', '_', full_category_name)
        full_category_descrption = category['description']
        category_description = re.sub(r'[:/\\?*“”<>|""]', '_', full_category_descrption)
        # os.path.join("..", "Aim_menu", "food_panda", f"{store_name}", f"{category_name}")
        if not os.path.exists(os.path.join("..", "Aim_menu", "food_panda", f"{store_name}", f"{category_name}")):
            os.makedirs(os.path.join("..", "Aim_menu", "food_panda", f"{store_name}", f"{category_name}"))
        if products_list is None:
            logging.info("category：{name}，no information".format(name=category['name']))
            continue
        for product in products_list:
            # result = {}
            # result.clear()
            item_name = re.sub(r'[:/\\?*“”<>|""]', '_', product.get('name'))
            total_category = category_name
            total_category_descrption = category_description
            total_item_name = item_name
            total_description = product.get('description')
            product_variations = product.get('product_variations')
            total_image = '' if product['images'] == [] else product['images'][0]['image_url']
            if total_image != '':
                item_image = total_image
                r = requests.get(item_image, timeout=180)
                image_path = os.path.join("..", "Aim_menu", "food_panda", f"{store_name}", f"{category_name}",
                                          f"{item_name}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(r.content)
            if product_variations is None:
                log.append("product ：{name}，no information".format(name=product.get('name')))
                logging.info("product ：{name}，no information".format(name=product.get('name')))
                continue
            if len(product_variations) == 1:
                logging.info("only one product ：{name}，no information".format(name=product.get('name')))
            elif len(product_variations) > 1:
                logging.info("multiple products ：{name}".format(name=product.get('name')))
                for pv in product_variations:
                    total_package_type = pv.get('name', '')
                    total_package_price = pv.get('price')
                    result = {'category': total_category, 'category_description': total_category_descrption,
                              'item_name': total_item_name, 'description': total_description, 'package_type': 'Combo',
                              'package_price': total_package_price, 'options': total_package_type}
                    food_panda_list.append(result)

            for pv in product_variations:
                total_package_type = pv.get('name', '')
                total_package_price = pv.get('price')
                result = {}
                result['category'] = total_category
                result['category_description'] = total_category_descrption
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
                topping_ids = pv['topping_ids']
                # result = {}
                # result['category'] = total_category
                # result['category_description'] = total_category_descrption
                # result['modifier_group'] = total_package_type
                # result['options'] = total_package_type
                # food_panda_list.append(result)
                if topping_ids:
                    for topping_id in topping_ids:
                        topping = toppings.get(str(topping_id))
                        total_modifier_group = topping.get('name')
                        total_select_type = 'Single' if topping.get('quantity_maximum') == 1 else 'Multiple'
                        if topping.get('quantity_minimum') == topping.get('quantity_maximum') == 1:
                            total_required_or_not = "TRUE"
                        else:
                            total_required_or_not = "FALSE"

                        total_min_available = topping.get('quantity_minimum')
                        total_max_available = topping.get('quantity_maximum')
                        options = topping['options']
                        for op in options:
                            total_options = op.get('name')
                            total_options_price = op.get('price')
                            result = {}
                            result['category'] = total_category
                            result['category_description'] = total_category_descrption
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

    food_panda_excel_list = []
    i = 0
    while i < len(food_panda_list):
        excel_language = variables.get('language', 'EN')
        excel_outlet_id = ''
        excel_outlet_services = ''
        excel_over_write = ''
        excel_category_name_en = (food_panda_list[i]).get('category') if isEn(variables) else ''
        excel_category_name_th = (food_panda_list[i]).get('category') if isTh(variables) else ''
        excel_category_name_cn = (food_panda_list[i]).get('category') if isCn(variables) else ''
        excel_category_sku = ''
        excel_category_description_en = (food_panda_list[i]).get('category_description') if isEn(variables) else ''
        excel_category_description_th = (food_panda_list[i]).get('category_description') if isTh(variables) else ''
        excel_category_description_cn = (food_panda_list[i]).get('category_description') if isCn(variables) else ''
        excel_item_name_en = (food_panda_list[i]).get('item_name') if isEn(variables) else ''
        excel_item_name_th = (food_panda_list[i]).get('item_name') if isTh(variables) else ''
        excel_item_name_cn = (food_panda_list[i]).get('item_name') if isCn(variables) else ''
        excel_item_sku = ''
        excel_item_image = (food_panda_list[i]).get('item_name') + '.jpg'
        excel_description_en = (food_panda_list[i]).get('description') if isEn(variables) else ''
        excel_description_th = (food_panda_list[i]).get('description') if isTh(variables) else ''
        excel_description_cn = (food_panda_list[i]).get('description') if isCn(variables) else ''
        excel_conditional_modifier_group = (food_panda_list[i]).get('package_type')
        excel_conditional_modifier = ''
        excel_item_price = (food_panda_list[i]).get('package_price')

        excel_modifier_group_en = (food_panda_list[i]).get('modifier_group') if isEn(variables) else ''
        excel_modifier_group_th = (food_panda_list[i]).get('modifier_group') if isTh(variables) else ''
        excel_modifier_group_cn = (food_panda_list[i]).get('modifier_group') if isCn(variables) else ''
        excel_modifier_group_sku = ''
        excel_modifier_group_description_en = ''
        excel_modifier_group_description_th = ''
        excel_modifier_group_description_cn = ''
        excel_select_type = (food_panda_list[i]).get('select_type')
        excel_required_or_not = (food_panda_list[i]).get('required_or_not')
        excel_min_available = (food_panda_list[i]).get('min_available')
        excel_max_available = (food_panda_list[i]).get('max_available')

        excel_modifier_en = (food_panda_list[i]).get('options') if isEn(variables) else ''
        excel_modifier_th = (food_panda_list[i]).get('options') if isTh(variables) else ''
        excel_modifier_cn = (food_panda_list[i]).get('options') if isCn(variables) else ''
        excel_modifier_sku = ''
        excel_modifier_description_en = ''
        excel_modifier_description_th = ''
        excel_modifier_description_cn = ''
        excel_options_price = (food_panda_list[i]).get('options_price')

        food_panda_excel_list.append(
            [excel_language, excel_outlet_id, excel_outlet_services, excel_over_write,
             excel_category_name_en, excel_category_name_th, excel_category_name_cn, excel_category_sku,
             excel_category_description_en, excel_category_description_th, excel_category_description_cn,
             excel_item_name_en, excel_item_name_th, excel_item_name_cn, excel_item_sku, excel_item_image,
             excel_description_en, excel_description_th, excel_description_cn, excel_conditional_modifier_group,
             excel_conditional_modifier, excel_item_price,
             excel_modifier_group_en, excel_modifier_group_th, excel_modifier_group_cn, excel_modifier_group_sku,
             excel_modifier_group_description_en, excel_modifier_group_description_th,
             excel_modifier_group_description_cn,
             excel_select_type, excel_required_or_not, excel_min_available, excel_max_available,
             excel_modifier_en, excel_modifier_th, excel_modifier_cn, excel_modifier_sku,
             excel_modifier_description_en, excel_modifier_description_th, excel_modifier_description_cn,
             excel_options_price])
        i += 1
    #     	Outlet ID

    df = pd.DataFrame(food_panda_excel_list,
                      columns=["Language", "Outlet ID", "Outlet services", "Overwrite (Y/N)", "category_name_en",
                               "category_name_th",
                               "category_name_cn", "category_sku", "category_description_en",
                               "category_description_th",
                               "category_description_cn", "item_name_en", "item_name_th", "item_name_cn", "item_sku",
                               "item_image", "description_en", "description_th", "description_cn",
                               "conditional_modifier_group", "conditional_modifier", "item_price", "modifier_group_en",
                               "modifier_group_th", "modifier_group_cn", "modifier_group_sku",
                               "modifier_group_description_en", "modifier_group_description_th",
                               "modifier_group_description_cn", "select_type",
                               "required_or_not", "min_available", "max_available", "modifier_en",
                               "modifier_th", "modifier_cn", "modifier_sku", "modifier_description_en",
                               "modifier_description_th", "modifier_description_cn", "options_price"])
    df.index = range(1, len(df) + 1)
    xlsx_path = os.path.join(["..", "Aim_menu", "food_panda", f"{store_name}.xlsx"])
    if os.path.exists(xlsx_path):
        os.remove(xlsx_path)
    logging.info(xlsx_path)
    df.to_excel(xlsx_path, index_label="序号")
    log.append("Collection complete")
    logging.info("Collection complete")
    return log

# if __name__ == '__main__':
#     test_url = 'https://www.foodpanda.hk/restaurant/v3iw/bakeout-homemade-koppepan'
#     parse_foodpanda(test_url)
