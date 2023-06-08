from urllib.parse import urlparse


def parse(url):
    result = {}

    type_dict = {
        'foodgrab': 'food.grab.com',
        'foodpanda': 'foodpanda'
    }
    parse_result = urlparse(url)
    # print(parse_result)
    for k, v in type_dict.items():
        if v in parse_result.netloc:
            result['type'] = k

    if result.get('type') == 'foodgrab':
        return parse_foodgrab(parse_result)
    elif result.get('type') == 'foodpanda':
        return parse_foodpanda(parse_result)

    return result


def parse_foodgrab(parse_result):
    result = {'type': 'foodgrab'}
    url_path = parse_result.path
    id = url_path.split('/')[-1]
    if id == '':
        id = url_path.split('/')[-2]
    result['country'] = url_path.split('/')[1]
    result['language'] = url_path.split('/')[2].upper()
    result['id'] = id
    return result


def parse_foodpanda(parse_result):
    result = {'type': 'foodpanda'}
    url_path = parse_result.path
    lan = url_path.split('/restaurant')[0]
    result['country'] = parse_result.netloc.split('.')[-1]
    result['language'] = 'EN' if lan == '' else lan.replace('/', '').upper()
    result['id'] = url_path.split('restaurant/')[1].split('/')[0]

    return result


def isEn(variables):
    if variables.get('language', 'EN') == 'EN':
        return True
    else:
        return False


def isCn(variables):
    if variables.get('language', 'EN') == 'CN':
        return True
    else:
        return False


def isTh(variables):
    if variables.get('language', 'EN') == 'TH':
        return True
    else:
        return False

# if __name__ == '__main__':
# print(url_parse('https://food.grab.com/sg/en/restaurant/mcdonald-s-jurong-green-cc-delivery/SGDD04996'))
# print(url_parse('https://food.grab.com/my/en/restaurant/hominsan-pavilion-non-halal-delivery/MYDD12622'))
# print(url_parse('https://food.grab.com/ph/en/restaurant/s-r-new-york-style-pizza-newport-delivery/PHGFSTI000000wz'))
# print(url_parse('https://food.grab.com/th/en/restaurant/%E0%B8%A3%E0%B8%B0%E0%B8%86%E0%B8%B1%E0%B8%87%E0%B9%82%E0%B8%A0%E0%B8%8A%E0%B8%99%E0%B8%B2%E0%B8%8B%E0%B8%B5%E0%B8%9F%E0%B8%B9%E0%B9%89%E0%B8%94%E0%B8%AA%E0%B9%8C-%E0%B9%81%E0%B8%82%E0%B8%A7%E0%B8%87%E0%B8%A8%E0%B8%B4%E0%B8%A3%E0%B8%B4%E0%B8%A3%E0%B8%B2%E0%B8%8A-delivery/3-C3A2TCJUWGLXCX'))
# print(url_parse('https://food.grab.com/vn/en/restaurant/ph%C3%AA-la-th%C3%A0nh-th%C3%A1i-delivery/5-C3KYLZMECGKDGN'))
# print(url_parse('https://food.grab.com/id/en/restaurant/dcrepes-delica-delipark-foodcourt-delivery/6-C22WJCMCUBNTGX'))
# print(url_parse('https://www.foodpanda.sg/restaurant/x02f/la-way-mala-hotpot-and-chinese-cuisine-orchard-towers'))
# print(url_parse('https://www.foodpanda.sg/zh/restaurant/x02f/la-way-mala-hotpot-and-chinese-cuisine-orchard-towers'))
# print(url_parse('https://www.foodpanda.my/restaurant/vrkv/zhong-qing-jiang-hu-cai-chinese-chongqing'))
# print(url_parse('https://www.foodpanda.ph/restaurant/s5no/chowking-moa-one-ecom'))
# print(url_parse('https://www.foodpanda.co.th/restaurant/z6kk/took-lae-dee-sukhumvit-soi-16'))
# print(url_parse('https://www.foodpanda.hk/restaurant/v3iw/bakeout-homemade-koppepan'))
# print(url_parse('https://www.foodpanda.com.tw/restaurant/w4ws/ji-ye-jia-yoshinoya-tai-bei-tai-da-dian'))
