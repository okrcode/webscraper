import requests
import lxml.html
from os import path
import csv
import json
import random
import pandas as pd


headers = {
    'authority': 'www.tripadvisor.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-full-version-list': '"Chromium";v="106.0.5249.119", "Google Chrome";v="106.0.5249.119", "Not;A=Brand";v="99.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}



def luminati_proxy(area=''):
    if 1:
        if area == 'us':
            username = 'lum-customer-propre-zone-static-country-us'
        elif area == 'jp':
            username = 'lum-customer-propre-zone-static-country-jp'
        else:
            username = 'lum-customer-propre-zone-static'

        password = 'dpocilp1igdr'
        port = 22225
        session_id = random.random()
        super_proxy_url = (
                'http://%s-session-%s:%s@zproxy.lum-superproxy.io:%d' % (username, session_id, password, port))
    else:
        super_proxy_url = '52.192.176.74:24000'

    proxies = {"http": super_proxy_url, 'https': super_proxy_url}
    # logger.info("use proxy")
    # logger.info("proxy setting : {}".format(proxies))
    return {}

def make_csv(final_arr,csvPath):
    keys = final_arr[0].keys()

    with open(csvPath, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_arr)

def get_res(url,proxies):
    retry = True
    cnt = 0
    res = None
    while retry:
        cnt += 1
        try:
            res = requests.get(url,headers=headers,proxies=proxies,timeout=30)
            retry = False
        except:
            print("retrying........")
            proxies = luminati_proxy("us")
            if cnt >= 3:
                retry = False
    return res,proxies




def get_data(url): 

    proxies = luminati_proxy("us")

    #url = "https://www.tripadvisor.com/Hotels-g293916-Bangkok-Hotels.html"

    #res = requests.get(url,headers=headers,proxies=proxies)
    # res,proxies = get_res(url,proxies)
    # dom= lxml.html.fromstring(res.text)
    # nodes = dom.xpath("//div[contains(@class,'listing_title')]/a/@href")

    # total_count = dom.xpath("//div/@data-main-list-match-count")[0]
    # try:
    #     pages = int(int(total_count)/30)
    # except:
    #     pages = 1
    offset = 4980
    pages = 15
    page_array = []
    #page_array.append(url)
    for i in range(pages):
        first_val,end_val = "-".join(url.split("-")[0:-2]),"-".join(url.split("-")[-2:])
        #page_url = f"https://www.tripadvisor.com/Hotels-g293916-oa{offset}-Bangkok-Hotels.html"
        page_url = f"{first_val}-oa{offset}-{end_val}"
        offset += 30
        page_array.append(page_url)

    final_arr = []
    for page_url in page_array:
        print(page_url)
        try:
            try:
                #page_res = requests.get(page_url,headers=headers,proxies=proxies)
                page_res,proxies = get_res(page_url,proxies)
                if not page_res:
                    continue
                page_dom= lxml.html.fromstring(page_res.text)
            except:
                proxies = luminati_proxy("us")
                print("errorrrrr...page....",page_url)
                continue
            nodes = page_dom.xpath("//div[contains(@class,'listing_title')]/a/@href")
            proxies = luminati_proxy("us")
            for node in nodes:
                node_url = "https://www.tripadvisor.com" + node
                #print(node_url)
                try:
                    #pro_res = requests.get(node_url,headers=headers,proxies=proxies)
                    pro_res,proxies = get_res(node_url,proxies)
                    if not pro_res:
                        continue
                    pro_dom = lxml.html.fromstring(pro_res.text)
                except:
                    proxies = luminati_proxy("us")
                    print("errorrrrr...url....",node_url)
                    continue
                try:
                    hotel_name = pro_dom.xpath("//h1[@id='HEADING']/text()")[0]
                except:
                    hotel_name = ""
                    print("errorr.....................")
                    continue
                source_url = node_url
                try:
                    hotel_class = pro_dom.xpath("//div[contains(@class,'S2')][contains(.,'HOTEL CLASS')]//following::div/span/svg/@aria-label")[0]
                except:
                    hotel_class = ""
                try:
                    address = pro_dom.xpath("//span[contains(@class,'map')]//following-sibling::span//text()")[0]
                except:
                    address = ""

                try:
                    lat = pro_dom.xpath("substring-before(substring-after(substring-after(//script[contains(.,'pageMa')][contains(.,'latitude')],'latitude'),':'),',')").replace('"','')
                    lon = pro_dom.xpath("substring-before(substring-after(substring-after(//script[contains(.,'pageMa')][contains(.,'longitude')],'longitude'),':'),',')").replace('"','')
                except:
                    lat = ""
                    lon = ""
                try:
                    number_of_room = pro_dom.xpath("//th[contains(.,'NUMBER OF ROOMS')]//following-sibling::td//text()|//div[contains(@id,'ABOUT_TAB')]//div/div[contains(.,'NUMBER OF ROOMS')]/following-sibling::div//text()")[0]
                except:
                    number_of_room = ""
                try:
                    official_url_node = pro_dom.xpath("substring-before(substring-after(//script[contains(.,'lightboxClickUrl')],'lightboxClickUrl'),'}')").replace('SOID',"CLD").replace('"','').replace(":","").replace("\\","")
                    if official_url_node:
                        official_url_node = "https://www.tripadvisor.com" + official_url_node
                        r = requests.get(official_url_node,headers=headers)
                        redir_dom= lxml.html.fromstring(r.text)
                        official_url = redir_dom.xpath("substring-before(substring-after(//script[contains(.,'location.href = ')],'location.href = '),'; }')").replace('"',"")
                    else:
                        official_url = ""
                except:
                    official_url = ""
                try:
                    price_range = [int(i.replace(",","")) for i in pro_dom.xpath('//div[@id="DEALS"]//a/@data-pernight')]
                    price_range.sort()
                    minprice  = f"${price_range[0]}"
                    maxprice  = f"${price_range[-1]}"

                except:
                    try:
                        price_range = "".join(pro_dom.xpath("//div[contains(@id,'ABOUT_TAB')]//div/div[contains(.,'PRICE RANGE')]//following-sibling::div//text()")[0:3])
                        minprice = price_range.split("-")[0]
                        maxprice = price_range.split("-")[-1]
                    except:
                        price_range = ""
                        minprice = ""
                        maxprice = ""
                dict_data = {"hotel_name":hotel_name,"source_url":source_url,"official_url":official_url,"hotel_class":hotel_class,
                            "minprice":minprice,"maxprice":maxprice,"address":address,"lat":lat,"lon":lon,"number_of_room":number_of_room,
                            "number_of_floor":"","year_property_opened":"","most_recent_renovation":""
                }
                final_arr.append(dict_data)
        except:
            continue
            print("aaaa")
    return final_arr


if __name__ == "__main__":
    
    # json_path = path.join(path.abspath(path.dirname(__file__)), "trip_advser_city_url.json")
    # with open(json_path, 'r') as datafile:
    #     data = json.load(datafile)
    data = ["https://www.tripadvisor.com/Hotels-g293925-Ho_Chi_Minh_City-Hotels.html"]
    #df_url_list = pd.read_json(path.join(path.abspath(path.dirname(__file__)), "trip_advser_city_url.json"), encoding='utf-8',index=False)
    for url in data:
        city_name = url.replace("-Hotels.html","").split("-")[-1]
        csv_path = f"tripad_{city_name}_city_new1_12.csv"
        array_val = get_data(url)
        df = pd.DataFrame(array_val)
        df.to_csv(csv_path, index=False,encoding='utf-8-sig')
        #make_csv(array_val,csv_path)


# csvPath = "tripad_ban.csv"
