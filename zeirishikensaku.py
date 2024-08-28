# url https://www.zeirishikensaku.jp/sch/zs_sch5.asp
import requests
import lxml.html
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import codecs
import csv
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

def make_url(page, hidchkGS_value, state_address):
    return f"hidCurrentPage={page}&hidOrder=&hidTorokuno=&hidTorokuno2=&hidCurrentForm=3&hidMode=1&hidNmKanji=&hidNmKana=&hidTorokuGENGO=&hidTorokuYY1=&hidTorokuYY2=&hidTorokuMM=&hidTorokuDD1=&hidTorokuDD2=&hidZeikai=&hidSextype=0&hidStateAddress={state_address}&hidSeireiAddress=&hidCityAddress=&hidJimname=&hidRiko=&hidchkGS={hidchkGS_value}&hidchkGM="

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,kn;q=0.7,ja;q=0.6',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.zeirishikensaku.jp',
    'priority': 'u=0, i',
    'referer': 'https://www.zeirishikensaku.jp/sch/zs_lst1.asp',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def get_initial_cookies():
    c_res = requests.get("https://www.zeirishikensaku.jp/sch/zs_sch3.asp", headers=headers)
    return dict(c_res.cookies)

def fetch_data1(hidchkGS_value, state_address, cookies):
    page = 1
    result = []
    while True:
        url = make_url(page, hidchkGS_value, state_address)
        response = requests.post('https://www.zeirishikensaku.jp/sch/zs_lst1.asp', cookies=cookies, headers=headers, data=url)
        
        try:
            dom = lxml.html.fromstring(response.text)
        except lxml.etree.ParserError:
            print(f"Empty or invalid response for hidchkGS_value: {hidchkGS_value} on page {page}. Updating cookies and retrying.")
            cookies = get_initial_cookies()
            response = requests.post('https://www.zeirishikensaku.jp/sch/zs_lst1.asp', cookies=cookies, headers=headers, data=url)
            try:
                dom = lxml.html.fromstring(response.text)
            except lxml.etree.ParserError:
                print(f"Retry failed for hidchkGS_value: {hidchkGS_value} on page {page}.")
                break
        
        td_elements = dom.xpath("//td[@class='cell_2'][1]")
        if not td_elements:
            print(f"No data found for hidchkGS_value: {hidchkGS_value} on page {page}. Moving to next hidchkGS_value.")
            break  
        
        for td in td_elements:
            result.append(td.text_content().strip())
        
        page += 1
    return result

cookies = get_initial_cookies()
# this is prefectures
state_addresses = ['%96k%8AC%93%B9', '%90%C2%90X%8C%A7']

# this is check boxes
hidchkGS_values = ["001%3A001", 
                   "002%3A001", "003%3A001", "004%3A001", "005%3A001","005%3A002","006%3A001","006%3A002","006%3A003",
                   "006%3A004","006%3A005","006%3A006","006%3A007","006%3A008","006%3A009","006%3A010",
                   "007%3A001","008%3A001","008%3A002","008%3A003",
                   "009%3A001","009%3A002","009%3A003","009%3A004",
                   "010%3A001","010%3A002","010%3A003","010%3A004","010%3A005","010%3A006","010%3A007",
                   "011%3A001","011%3A002","011%3A003","011%3A004",
                   "012%3A001","012%3A002",  "013%3A001","013%3A002","013%3A003", "014%3A001","014%3A002", "015%3A001","015%3A002","016%3A001",
                   "017%3A001","017%3A002","017%3A003","017%3A004","017%3A005","017%3A006","017%3A007","017%3A008","017%3A009",
                   "018%3A001","018%3A002","018%3A003",
                   ]

id_list = []

for state_address in state_addresses:
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_hidchkGS = {executor.submit(fetch_data1, value, state_address, cookies): value for value in hidchkGS_values}
        for future in as_completed(future_to_hidchkGS):
            hidchkGS_value = future_to_hidchkGS[future]
            try:
                ids = future.result()
                id_list.extend(ids)
            except Exception as exc:
                print(f'{hidchkGS_value} generated an exception: {exc}')
            
# Function to get cookies using Selenium
def get_cookies_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--safebrowsing-disable-auto-update")
    chrome_options.add_argument("--enable-automation")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)

    try:
        driver.get("https://www.zeirishikensaku.jp/sch/zs_sch5.asp")

        driver.execute_script("ken_select('北海道')")

        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='chkGS' and @value='001:001:Ａ　農業:農業:0']"))
        )
        checkbox.click()

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='javascript:onClick=jf_SerchClick();']"))
        )
        submit_button.click()

        cookies = driver.get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        return cookies_dict

    finally:
        driver.close()
# Headers for the request
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,kn;q=0.7,ja;q=0.6',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.zeirishikensaku.jp',
    'priority': 'u=0, i',
    'referer': 'https://www.zeirishikensaku.jp/sch/zs_lst1.asp',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}


def replace_line_breaks(text):
    return ','.join([line.strip() for line in text.split('\n') if line.strip()])

def fetch_data(id, initial_cookies):
    data = f'hidCurrentPage=&hidOrder=&hidTorokuno=&hidTorokuno2={id}&hidCurrentForm=3&hidMode=1&hidNmKanji=&hidNmKana=&hidTorokuGENGO=&hidTorokuYY1=&hidTorokuYY2=&hidTorokuMM=&hidTorokuDD1=&hidTorokuDD2=&hidZeikai=&hidSextype=0&hidStateAddress=%96k%8AC%93%B9&hidSeireiAddress=&hidCityAddress=&hidJimname=&hidRiko=&hidchkGS=001%3A001%3A%82%60%81%40%94_%8B%C6%3A%94_%8B%C6%3A0&hidchkGM='
    # print(data)
    cookies = initial_cookies

    
    while True:
        pro_res = requests.post('https://www.zeirishikensaku.jp/sch/zs_dt0.asp', cookies=cookies, headers=headers, data=data)
        if not pro_res.text.strip():
            print("Response is empty. Updating cookies and retrying.")
            new_cookies1 = get_cookies_selenium()
            new_cookies = new_cookies1
            initial_cookies.update(new_cookies)
        else:
            break
    decode = codecs.decode(bytes(pro_res.text, 'latin-1'), 'shift_jis')
    pro_dom = lxml.html.fromstring(decode)
 

    dict_data = {}

    try:
        # Extract data from table 1
        keys1 = pro_dom.xpath("//table[@class='table'][1]//td[@class='CELL_HEADER']/text()")
        values1 = pro_dom.xpath("//table[@class='table'][1]//td[contains(@class,'cell_')]")

        values1_text = [value.text.strip() if value.text and value.text.strip() != "" else None for value in values1]

        zipped_data = zip(keys1, values1_text)
        # Iterate through zipped data
        for key, value in zipped_data:
            if value is None or value.strip() == "":
                dict_data[key.strip()] = None
            else:
                dict_data[key.strip()] = value.strip()

    except Exception as e:
        print(f"An error occurred while extracting data from table 1: {e}")

    try:
        # Extract data from table 2
        keys2 = pro_dom.xpath("//table[@class='table'][2]//td[@class='CELL_HEADER']/text()")
        values2 = pro_dom.xpath("//table[@class='table'][2]//td[contains(@class,'cell_')]/text()")
        for key, value in zip(keys2, values2):
            dict_data[key.strip()] = value.strip() if value.strip() else None
    except Exception as e:
        print(f"An error occurred while extracting data from table 2: {e}")

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ａ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ａ　農業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ａ　農業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｂ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｂ　林業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｂ　林業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｃ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｃ　漁業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｃ　漁業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｄ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｄ　鉱業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｄ　鉱業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｅ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｅ　建設業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｅ　建設業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｆ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｆ　製造業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｆ　製造業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｇ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｇ　電気・ガス・熱供給・水道業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｇ　電気・ガス・熱供給・水道業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｈ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｈ　情報通信業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｈ　情報通信業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｉ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｉ　運輸業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｉ　運輸業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｊ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｊ　卸売・小売業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｊ　卸売・小売業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｋ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｋ　金融・保険業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｋ　金融・保険業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｌ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｌ　不動産業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｌ　不動産業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｍ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｍ　飲食店・宿泊業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｍ　飲食店・宿泊業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｎ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｎ　医療・福祉"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｎ　医療・福祉"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｏ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｏ　教育・学習支援"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｏ　教育・学習支援"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｐ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｐ　複合サービス事業"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｐ　複合サービス事業"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｑ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｑ　サービス業（他に分類されないもの）"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｑ　サービス業（他に分類されないもの）"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), 'Ｒ')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["Ｒ　その他"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["Ｒ　その他"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), '個　人　税務代理・書類の作成・相談')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["個　人　税務代理・書類の作成・相談"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["個　人　税務代理・書類の作成・相談"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), '法　人　税務代理・書類の作成・相談')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["法　人　税務代理・書類の作成・相談"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["法　人　税務代理・書類の作成・相談"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), '個人法人共通　税務代理・書類の作成・相談')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["個人法人共通　税務代理・書類の作成・相談"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["個人法人共通　税務代理・書類の作成・相談"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), '会計業務')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["会計業務"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["会計業務"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), '経営相談等')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["経営相談等"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["経営相談等"] = None

    try:
        raw_text = pro_dom.xpath("//tr[td[@class='cell_header']/b[contains(text(), '公益的業務等')]]/td[@class='cell_2']")[0].text_content().strip()
        dict_data["公益的業務等"] = replace_line_breaks(raw_text)
    except Exception as e:
        dict_data["公益的業務等"] = None
    
    
    dict_data["ymd"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return dict_data

def main(ids):
    initial_cookies = get_cookies_selenium()

    # Fetch data for all IDs using multithreading
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda id: fetch_data(id, initial_cookies), ids))
    csv_file_path = 'Zextracted_data.csv'

    # Define the fieldnames based on the keys of the first dictionary in results
    fieldnames = results[0].keys() if results else []

    # Write data to CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:  
        # Use utf-8-sig to handle Unicode characters properly
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write rows
        writer.writerows(results)

    print("Data has been saved to", csv_file_path)

# Call the main function
if __name__ == "__main__":
    main(id_list)
            
