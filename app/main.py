import requests
import json
from lxml import html
import datetime
import time
import csv
import os.path
import os
import websockets
import asyncio
import threading
import signal

from dotenv import load_dotenv
load_dotenv()

from core.sendgrid import send_email
from core.telegram import send_message
from core.zipfile import compact_file


cookies = {}
headers = {}


def extract_data(link):
    data = []
    response = requests.get(link, cookies=cookies, headers=headers)
    tree = html.fromstring(response.content)
    body_json = json.loads(tree.xpath("/html/body/script[1]/text()")[0].replace('window.__INITIAL_CONFIG__ = ',''))
    
    try:
        prices_by_sku = body_json['viewData']['price']['bySkuId']
    except:
        prices_by_sku = None

    skus = body_json['viewData']['skus']['byId']
    features = body_json['viewData']['features']
    Review_Stars = body_json['viewData']['reviews']['averageRating']
    Review_Count = body_json['viewData']['reviews']['numberOfReviews']
    productName = body_json['viewData']['productName']

    if len(skus) == 0:
        tmp = {
                'URL': link,
                'SKU': 'N/A',
                'Item#': features[-1].split('#')[-1],
                'Title': productName,
                'Color': 'N/A',
                'Size': 'N/A',
                'Available_QTY': 'N/A',
                'Available': 'Not available',
                'Date': datetime.date.today().isoformat(),
                'Currency': 'USD',
                'Price': 999,
                'Review_Count': Review_Count,
                'Review_Stars': Review_Stars,
        }
        print(tmp)
        data.append(tmp)
    else:
        for sku in skus:
            if prices_by_sku == None:
                currencyCode = 'USD'
                price = 'SOULD OUT'
            else:
                currencyCode = prices_by_sku[sku]['regular']['price']['currencyCode']
                price = f"{prices_by_sku[sku]['regular']['price']['units']}."
                price = f"{price}{prices_by_sku[sku]['regular']['price']['nanos']}"

            if skus[sku]['totalQuantityAvailable'] == 0:
                available = f"Not available in {skus[sku]['colorDisplayValue']}"
            elif skus[sku]['totalQuantityAvailable'] == 1:
                available = 'Only 1 left'
            elif skus[sku]['totalQuantityAvailable'] == 2:
                available = 'Only 2 left'
            elif skus[sku]['totalQuantityAvailable'] < 6:
                available = 'Only a few left'
            else:
                available = 'In Stock'

            tmp = {
                'URL': link,
                'SKU': sku,
                'Item#': features[-1].split('#')[-1],
                'Title': productName,
                'Color': skus[sku]['colorDisplayValue'],
                'Size': skus[sku]['sizeDisplayValue'],
                'Available_QTY': skus[sku]['totalQuantityAvailable'],
                'Available': available,
                'Date': datetime.date.today().isoformat(),
                'Currency': currencyCode,
                'Price': price,
                'Review_Count': Review_Count,
                'Review_Stars': Review_Stars,
            }
            print(tmp)
            data.append(tmp)
    time.sleep(10)
    return data

def get_detail():    
    f_name = f"{os.getenv('PATH_RESULT')}nordstrom_{datetime.date.today().isoformat()}.csv"
    head_lines = os.path.isfile(f_name)
    f = open(f"{os.getenv('PATH_RESULT')}toDo.txt", "r")
    lines = f.read().split('\n')[:4]
    f.close()
    while len(lines) > 0:
        line = lines.pop()
        if line != '':
            try:
                row = extract_data(line)
                if len(row) > 0:
                    with open(f_name, 'a') as f:
                        writer = csv.DictWriter(f, fieldnames=row[0])
                        if head_lines == False:
                            head_lines = True
                            writer.writeheader()
                        writer.writerows(row)
                else:
                    with open(f"{os.getenv('PATH_RESULT')}no_records_found.txt", 'a') as f:
                        f.write(f'{line}\n')

                with open(f"{os.getenv('PATH_RESULT')}toDo.txt", 'w') as f:
                    for link in lines:
                        f.write(f'{link}\n')
            except Exception as e:
                print(e)
                lines.append(line)
                wait_variables()
                time.sleep(30)
    return f_name

def wait_variables():
    global headers, cookies
    os.system("ps aux | grep -i chrome | awk '{print $2}' | xargs kill -9")
    cookies = {}
    headers = {}
    time.sleep(2)
    os.system("google-chrome --no-sandbox --args --incognito \"https://www.nordstrom.com/brands/la-femme--5309?origin=productBrandLink&page=1\"")
    max_try = 10
    while cookies == {} and max_try > 0:
        print('Wait variables')
        time.sleep(4)
        max_try = max_try -1
    if max_try == 0:
        time.sleep(30)
        wait_variables()
    os.system("ps aux | grep -i chrome | awk '{print $2}' | xargs kill -9")

def get_links():
    page=1
    time.sleep(5)
    with open(f"{os.getenv('PATH_RESULT')}toDo.txt", 'w') as f:
        while True: 
            print('Buscando urls...')
            time.sleep(2)
            url = f'https://www.nordstrom.com/brands/la-femme--5309?origin=productBrandLink&page={page}'
            response = requests.get(url, cookies=cookies, headers=headers)
            tree = html.fromstring(response.content)
            header = tree.xpath("//main//header//span")
            if len(header) == 0:
                wait_variables()
            else:
                articles = tree.xpath("//article")
                links = [f"https://www.nordstrom.com{article.xpath('h3/a/@href')[0]}" for article in articles]
                if(len(links) == 0):
                    break
                print(url)
                for link in links:
                    f.write(f'{link}\n')
                page = page + 1

def main():
    send_message(f"Start Nordstrom process...")
    get_links()
    f_name = get_detail()
    compacted_file = compact_file(f_name)
    send_email(
        os.getenv('EMAIL_TO'),
        f"Data updated [{f_name.split('/')[-1]}]",
        '<strong>Data from web site Nordstrom</strong>',
        compacted_file)

    send_message(f"File sent: {f_name.split('/')[-1]}.")

    os.kill(os.getpid(),signal.SIGKILL)


async def handler(websocket, path):
    global headers, cookies
    data = await websocket.recv()
    json_data  = json.loads(data)
    if json_data['cookie']:
        cookies = {'user-agent': json_data['cookie'] }
    if json_data['agent']:
        headers = {'user-agent': json_data['agent'] }
    await websocket.send('Done')
    os.system("ps aux | grep -i chrome | awk '{print $2}' | xargs kill -9")
    if json_data['close']:
       wait_variables()

start_server = websockets.serve(handler, "0.0.0.0", 8011)
asyncio.get_event_loop().run_until_complete(start_server)
threading.Thread(target=main).start()
asyncio.get_event_loop().run_forever()

