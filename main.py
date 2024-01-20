import requests
import json
from lxml import html
import datetime
import time
import csv
import os.path
import os
from typing import Union
import subprocess
from threading import Thread
import uvicorn

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import typing
class Item(BaseModel):
    cookie: str
app = FastAPI()

cookies = {}

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def set_cookies(cookie_string):
    global cookies
    cookies = cookie_string
    print(cookies)

def extract_data(link):
    data = []
    response = requests.get(link, cookies=cookies, headers=headers)
    print(link)
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
                'Price': 'SOULD OUT',
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



def open_brave():
    close_brave()
    time.sleep(2)
    os.system("open -na \"Brave Browser.app\" --args --incognito \"https://www.nordstrom.com/brands/la-femme--5309?origin=productBrandLink&page=1\"")

def close_brave():
    os.system("ps aux | grep -i brave | awk '{print $2}' | xargs kill -9")




# 185232
# 185247


# schedulle = 180000
# dif       = 20000


schedulle = 191100
dif       =  20000
job_day   =  5

currentDateAndTime = datetime.datetime.now()
print(currentDateAndTime.weekday())

def get_detail():
    while True:
        currentDateAndTime = datetime.datetime.now()
        currentTime = currentDateAndTime.strftime("%H%M%S")
        if currentDateAndTime.weekday() == job_day:
            running = os.path.isfile('running.dat')
            if int(currentTime) > (int(schedulle) + dif) and running == True:
                os.remove('running.dat') 

            if int(currentTime) > int(schedulle) and int(currentTime) < (int(schedulle) + dif - 1)  and running == False:
                f = open("running.dat", "w")
                f.close()
                #get_links()
                cont = 0
                head_lines = os.path.isfile(f'nordstrom_{datetime.date.today().isoformat()}.csv')
                f = open("toDo.txt", "r")
                lines = f.read().split('\n')
                total = len(lines)
                f.close()
                while len(lines) > 0:
                    line = lines.pop()
                    if line != '':
                        try:
                            row = extract_data(line)
                            if len(row) > 0:
                                with open(f'nordstrom_{datetime.date.today().isoformat()}.csv', 'a') as f:
                                    writer = csv.DictWriter(f, fieldnames=row[0])
                                    if head_lines == False:
                                        head_lines = True
                                        writer.writeheader()
                                    writer.writerows(row)
                            else:
                                with open('no_records_found.txt', 'a') as f:
                                    f.write(f'{line}\n')

                            cont = cont + 1
                            with open('toDo.txt', 'w') as f:
                                for link in lines:
                                    f.write(f'{link}\n')
                            print(f"{cont}/{total}")
                        except Exception as e:
                            print(e)
                            lines.append(line)
                            open_brave()
                            time.sleep(30)
        print('Next....')
        time.sleep(2)   


def get_links():
    page=1
    with open('toDo.txt', 'w') as f:
        while True: 
            url = f'https://www.nordstrom.com/brands/la-femme--5309?origin=productBrandLink&page={page}'
            response = requests.get(url, cookies=cookies, headers=headers)
            tree = html.fromstring(response.content)
            header = tree.xpath("//main//header//span")
            if len(header) == 0:
                open_brave()
                time.sleep(30)
            else:
                articles = tree.xpath("//article")
                links = [f"https://www.nordstrom.com{article.xpath('h3/a/@href')[0]}" for article in articles]
                if(len(links) == 0):
                    break
                print(url)
                for link in links:
                    f.write(f'{link}\n')
                page = page + 1


thread = Thread(target=get_detail, args=())

@app.on_event("startup")
async def startup_event():
    thread.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/data")
async def post_dict(data: Item):
    global cookies
    for value in data.dict()['cookie'].split():
        key = value.split('=')[0]
        val = '='.join(value.split('=')[1:])
        cookies[f'{key}'] = val
    return {"status": "ok"}

@app.get("/stop")
def read_stop():
    return {"status": "ok"}

@app.get("/close")
def read_stop():
    close_brave()
    return {"status": "ok"}

@app.get("/shutdown")
def read_stop():
    graceful_shutdown()
    return {"status": "ok"}


if __name__ == "__main__":
    # Start the FastAPI application using uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)



