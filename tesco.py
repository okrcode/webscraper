import requests
import lxml.html
import pandas as pd
import json 

# Define headers for the HTTP requests to mimic a browser visit
headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.tesco.com',
    'priority': 'u=1, i',
    'referer': 'https://www.tesco.com/groceries/en-GB/shop/treats-and-snacks/all?_gl=1*1gy4qxx*_up*MQ..*_ga*MTY3NDIxODQzMS4xNzI0MzE5OTQ1*_ga_33B19D36CY*MTcyNDMxOTk0NS4xLjAuMTcyNDMxOTk0NS4wLjAuNjI0MTQ5MTE0&brand=CADBURY%2CWALKERS%2CTESCO&viewAll=brand',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',                      
    'x-queueit-ajaxpageurl': 'false',
    'x-requested-with': 'XMLHttpRequest',
}


# Function to get the total page count of products and the hash value required for subsequent requests
def get_page_count(headers):
    # Define the JSON payload for the initial request to fetch product information
    json_data = {
        'resources': [
            {
                'type': 'productsByCategory',
                'params': {
                    'query': {
                        '_gl': '1*1gy4qxx*_up*MQ..*_ga*MTY3NDIxODQzMS4xNzI0MzE5OTQ1*_ga_33B19D36CY*MTcyNDMxOTk0NS4xLjAuMTcyNDMxOTk0NS4wLjAuNjI0MTQ5MTE0',
                        'brand': 'CADBURY,WALKERS,TESCO,KINDER',
                        'viewAll': 'brand',
                    },
                    'superdepartment': 'treats-and-snacks',
                },
            },
        ],
        'sharedParams': {
            'superdepartment': 'treats-and-snacks',
            'query': {
                '_gl': '1*1gy4qxx*_up*MQ..*_ga*MTY3NDIxODQzMS4xNzI0MzE5OTQ1*_ga_33B19D36CY*MTcyNDMxOTk0NS4xLjAuMTcyNDMxOTk0NS4wLjAuNjI0MTQ5MTE0',
                'brand': 'CADBURY,WALKERS,TESCO,KINDER',
                'viewAll': 'brand',
            },
        },
        'requiresAuthentication': False,
    }
     # Send the POST request to retrieve the data
    response = requests.post('https://www.tesco.com/groceries/en-GB/resources', headers=headers, json=json_data)
    json_vals = response.json()
    try:
        hash_val = json_vals["trolleyContents"]["hash"]
    except:

        hash_val = json_vals["productsByCategory"]["hash"]
    pages = round(json_vals["productsByCategory"]["data"]["results"]["pageInformation"]["totalCount"]/24)
    return pages,hash_val

# Function to retrieve product details from a specific page
def get_res(headers,page,hash_val):
    # Define the JSON payload for the request to fetch product details
    json_data = {
        'resources': [
            {
                'type': 'productsByCategory',
                'params': {
                    'query': {
                        '_gl': '1*1gy4qxx*_up*MQ..*_ga*MTY3NDIxODQzMS4xNzI0MzE5OTQ1*_ga_33B19D36CY*MTcyNDMxOTk0NS4xLjAuMTcyNDMxOTk0NS4wLjAuNjI0MTQ5MTE0',
                        'brand': 'CADBURY,WALKERS,TESCO,KINDER',
                        'page': str(page),
                        'viewAll': 'brand',
                    },
                    'superdepartment': 'treats-and-snacks',
                },
                'hash': hash_val,
            },
        ],
        'sharedParams': {
            'superdepartment': 'treats-and-snacks',
            'referer': '/groceries/en-GB/shop/treats-and-snacks/all?_gl=1*1gy4qxx*_up*MQ..*_ga*MTY3NDIxODQzMS4xNzI0MzE5OTQ1*_ga_33B19D36CY*MTcyNDMxOTk0NS4xLjAuMTcyNDMxOTk0NS4wLjAuNjI0MTQ5MTE0&brand=CADBURY%2CWALKERS%2CTESCO%2CKINDER&viewAll=brand',
            'query': {
                '_gl': '1*1gy4qxx*_up*MQ..*_ga*MTY3NDIxODQzMS4xNzI0MzE5OTQ1*_ga_33B19D36CY*MTcyNDMxOTk0NS4xLjAuMTcyNDMxOTk0NS4wLjAuNjI0MTQ5MTE0',
                'brand': 'CADBURY,WALKERS,TESCO,KINDER',
                'page': str(page),
                'viewAll': 'brand',
            },
        },
        'requiresAuthentication': False,
    }
    # Send the POST request to retrieve the data for the specific page
    response = requests.post('https://www.tesco.com/groceries/en-GB/resources', headers=headers, json=json_data)
    json_vals = response.json()
    return json_vals

# Main URL to access the Tesco groceries page
main_url = "https://www.tesco.com/groceries/en-GB/shop/treats-and-snacks/all"
res = requests.get(main_url,headers=headers)
cookies_csrf = dict(res.cookies)["_csrf"]
dom = lxml.html.fromstring(res.text)
header_csrf_token = dom.xpath("//body/@data-csrf-token")

# Update headers with the CSRF token and cookies
headers["cookie"] = f"_csrf={cookies_csrf};"
headers["x-csrf-token"] = header_csrf_token[0]

# Retrieve the total number of pages and hash value
pages,hash_val = get_page_count(headers)
array_ids = []
for page in range(1,pages+1):
    print(f"Processing page: {page}")
    json_res = get_res(headers,page,hash_val)
    array_ids+=[i["product"]["id"] for i in json_res["productsByCategory"]["data"]["results"]["productItems"]]

# Loop through each product ID and retrieve its details
array_data = []
for ids in array_ids:
    print(f"Processing product ID: {ids}")          
    url = f"https://www.tesco.com/groceries/en-GB/products/{ids}"
    res = requests.get(url,headers=headers)
    dom = lxml.html.fromstring(res.text)

    # Parse product details from the page
    pro_details = json.loads(dom.xpath("//script[@type='application/ld+json']/text()")[0])
    details_val = [i for i in pro_details["@graph"] if "sku" in i.keys()][0]
    try:
        name = dom.xpath("//h1/text()")[0]
    except:
        name = details_val["name"]

    try:
        price = dom.xpath("//div[contains(@class, 'price__container')]//text()")[0]
    except:
        price = details_val["offers"]["price"]

    if "InStock" in details_val["offers"]["availability"]:
        availability = "In Stock"
    else:
        availability = "Out Of Stock"
    try:
        product_image = details_val["image"][0]
    except:
        imgs = []
        for img in dom.xpath("//img/@src"):
            imgs.append(""+ img)
        product_image= ' , '.join(imgs)


    # Extract nutritional information from the page
    energy_details = dom.xpath("//script[@type='application/discover+json']/text()")[0]
    json_enrgy = json.loads(energy_details)
    pro_key = [i for i in json_enrgy["mfe-orchestrator"]["props"]["apolloCache"].keys() if "ProductType" in i][0]
    enery_vals = json_enrgy["mfe-orchestrator"]["props"]["apolloCache"][pro_key]["details"]["nutrition"]
    [i.pop('__typename', None) for i in enery_vals]

    products_dict = {
            'URL': url,
            'Product Name': name,
            'Product Image': product_image,
            'Price': price,
            'Availability': availability,
            'Nutritional Information': enery_vals
        }
    array_data.append(products_dict)


# Initialize list to hold all rows
all_rows = []

# Loop through each product
for product in array_data:
    # First row: Product details
    all_rows.append([
        product['URL'],
        product['Product Name'],
        product['Product Image'],
        product['Price'],
        product['Availability'],
        'Typical Values',  # Nutritional Information header
        'Per 100 g', 'Per 5 Chunks (30 g)', '*Reference Intakes'
    ])
    
    # Subsequent rows: Nutritional Information
    for nutrition in product['Nutritional Information']:
        all_rows.append([
            '', '', '', '', '',  # Empty columns for product details
            nutrition['name'],
            nutrition['value1'],
            nutrition['value2'],
            nutrition['value3']
        ])
    
    # Append a blank row to separate products (optional)
    all_rows.append([''] * 9)

# Convert list of rows to DataFrame
columns = ['URL', 'Product Name', 'Product Image', 'Price', 'Availability',
           'Nutritional Information', 'Per 100 g', 'Per 5 Chunks (30 g)', '*Reference Intakes']
final_df = pd.DataFrame(all_rows, columns=columns)

final_df.to_excel('products_with_nutrition1.xlsx', index=False)

print("Excel file with multiple products created successfully.")
