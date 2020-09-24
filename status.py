import requests
import dateutil.parser as dparser
import re
import sys
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
import dateparser

config = {
    'out': '/var/www/rtx/index.html',
    'regenerate': 3, #in seconds,
    'log': '/home/iglocska/rtx/log.log',
    'max_days': 30
}

def execute():
    results = []
    results = alternate(results)
    results = caseking(results)
    results = proshop(results)
    results = mindfactory(results)
    # broken - loaded dynamically
    # results = computeruniverse(results)
    results = cyberport(results)
    fields = ['shop','name','price','availability']
    field_string = ''
    hits_string = ''
    for field in fields:
        field_string += f"<th>{field}</th>"
    head = '<link rel="stylesheet" href="bootstrap.css"><script src="bootstrap.js"></script>'
    head += '<meta http-equiv="refresh" content="1">'
    now = datetime.now()
    header_text = f"RTX scout, data updated @ {now}"
    hits = [];
    for pos, result in enumerate(results):
       if result['status'] == 'ok':
           try:
               testDate = dparser.parse(result['availability'], fuzzy=True, dayfirst=True)
           except:
               testDate = False
           if (testDate):
               now = datetime.now()
               if ((testDate - now).days > config['max_days']):
                   results[pos]['status'] = 'fail'
                   continue
           hits.append(result)
           hits_string += '<tr>'
           for field in fields:
               if field is 'availability':
                   hits_string += f"<td style=\"color:white;background-color:green;\">{result[field]}</td>"
               else:
                   hits_string += f"<td>{result[field]}</td>"
           hits_string += '</tr>'
    for result in results:
       if result['status'] != 'ok':
           hits_string += '<tr>'
           for field in fields:
               if field is 'availability':
                   hits_string += f"<td style=\"color:white;background-color:red;\">{result[field]}</td>"
               else:
                   hits_string += f"<td>{result[field]}</td>"
           field_string += '</tr>'
    count = len(hits)
    icon = ''
    if (count > 0):
        logHits(hits)
        icon = '<link rel="icon" type="image/png" href="warning.png">'
    print(f"\nChecks complete, {count} hits.")
    return f"<html><head>{head}{icon}</head><body><table><p>{header_text}</p><tr>{field_string}</tr>{hits_string}</table></body></html>"

def logHits(hits):
    if os.path.exists(config['log']):
        file_mode = 'a'
    else:
        file_mode = 'w'
    file = open(config['log'], file_mode)
    time = datetime.now()
    for hit in hits:
        file.write(f"\n{time}: Shop::{hit['shop']} - Status::{hit['availability']} - URL::{hit['url']}")
    file.close()


def alternate(results):
    r = requests.get('https://www.alternate.de/html/search.html?query=rtx+3080&x=0&y=0')
    if (r.status_code is 200):
        html = BeautifulSoup(r.text, 'html.parser')
        search_results = html.find_all('div', class_="listRow")
        for row in search_results:
            temp = {}
            product_link = row.find_all('a', class_="productLink")
            product_link = product_link[0]
            temp['shop'] = 'alternate'
            temp['url'] = product_link.get('href')
            name = product_link.get('title')
            temp['name'] = f"<a href=\"http://www.alternate.de/{temp['url']}\">{name}</a>"
            price = row.find_all('span', class_="price")
            price = price[0].text
            temp['price'] = int(re.findall("\d+", price)[0])
            stock_status = row.find_all('strong', class_="stockStatus")
            stock_status = stock_status[0]
            temp['availability'] = stock_status.string.strip()
            temp['status'] = 'ok'
            if (temp['availability'] == 'Liefertermin unbekannt'):
                temp['status'] = 'fail'
            if (temp['price'] > 500 and temp['price'] < 900):
                results.append(temp)        
    return results

def caseking(results):
    r = requests.get('https://www.caseking.de/search?sSearch=rtx3080')
    if (r.status_code is 200):
        html = BeautifulSoup(r.text, 'html.parser')
        search_results = html.find_all('div', class_="artbox")
        for row in search_results:
            temp = {}
            product_link = row.find_all('a', class_="producttitles")
            product_link = product_link[0]
            temp['shop'] = 'caseking'
            temp['url'] = product_link.get('href')
            name = product_link.get('title')
            temp['name'] = f"<a href=\"{temp['url']}\">{name}</a>"
            price = row.find_all('span', class_="price")
            price = price[0].text
            temp['price'] = int(re.findall("\d+", price)[0])
            stock_status = row.find_all('span', class_="frontend_plugins_index_delivery_informations")
            stock_status = stock_status[0]
            temp['availability'] = stock_status.string.strip()
            temp['status'] = 'ok'
            if (temp['availability'] == 'unbekannt'):
                temp['status'] = 'fail'
            if (temp['price'] > 500 and temp['price'] < 900):
                results.append(temp)        
    return results

def proshop(results):
    r = requests.get('https://www.proshop.de/Grafikkarte?pre=0&f~grafikkort_videoudganggrafikprocessorleverandor=nvidia-geforce-rtx-3080')
    if (r.status_code is 200):
        html = BeautifulSoup(r.text, 'html.parser')
        container = html.find_all(id="products")
        if (not container):
            return results
        container = container[0]
        search_results = container.find_all('li', class_="row")
        for row in search_results:
            temp = {}
            product_link = row.find_all('a', class_="site-product-link")
            product_link = product_link[0]
            temp['shop'] = 'proshop'
            temp['url'] = product_link.get('href')
            name = product_link.find_all('h2')[0].text
            temp['name'] = f"<a href=\"https://www.proshop.de/{temp['url']}\">{name}</a>"
            price = row.find_all('span', class_="site-currency-lg")
            price = price[0].text
            temp['price'] = int(re.findall("\d+", price)[0])
            stock_status = row.find_all('div', class_="site-stock-text")
            stock_status = stock_status[0]
            stock_status_icon = row.find_all('i', class_="site-icon-stock-in")
            temp['status'] = 'ok'
            if not stock_status_icon:
                stock_status_icon = row.find_all('i', class_="site-icon-stock-comming")
                if not stock_status_icon:
                    temp['status'] = 'fail'
            temp['availability'] = stock_status.string.strip()
            if (temp['price'] > 600 and temp['price'] < 900):
                results.append(temp)        
    return results
   
def mindfactory(results):
    r = requests.get('https://www.mindfactory.de/search_result.php?select_search=78247&search_query=rtx+3080')
    if (r.status_code is 200):
        html = BeautifulSoup(r.text, 'html.parser')
        container = html.find_all(id="bProducts")
        if not container:
            return results
        search_results = html.find_all('div', class_="p")
        for row in search_results:
            temp = {}
            product_link = row.find_all('a', class_="phover-complete-link")
            product_link = product_link[0]
            temp['shop'] = 'mindfactory'
            url = product_link.get('href')
            name = row.find_all('div', class_="pname")[0].string
            temp['url'] = url
            temp['name'] = f"<a href=\"{url}\">{name}</a>"
            price = row.find_all('div', class_="pprice")
            price = price[0].text
            temp['price'] = int(re.findall("\d+", price)[0])
            temp['status'] = 'ok'
            stock_status = row.find_all('span', class_="shipping1")
            if not stock_status:
                stock_status = row.find_all('span', class_="shipping2")
                if not stock_status:
                    stock_status = row.find_all('span', class_="shipping3")
                    if not stock_status:
                        temp['status'] = 'fail'
                        temp['availability'] = 'Unbekannt'
            if temp['status'] == 'ok':
                temp['availability'] = stock_status[0].string.strip()
            if (temp['price'] > 500 and temp['price'] < 900):
                results.append(temp)        
    return results

def computeruniverse(results):
    r = requests.get('https://www.computeruniverse.net/de/c/hardware-komponenten/grafikkarten-pci-express?refinementList%5Bfacets.Chipsatz.values%5D%5B0%5D=NVIDIA%C2%AE%20GeForce%20RTX%E2%84%A2%203080')
    if (r.status_code is 200):
        html = BeautifulSoup(r.text, 'html.parser')
        search_results = html.find_all('div', class_="at__product-display")
        for row in search_results:
            temp = {}
            product_link = row.find_all('a', class_="at__productListItemTitle")
            product_link = product_link[0]
            temp['shop'] = 'computeruniverse'
            temp['url'] = product_link.get('href')
            name = product_link.text
            temp['name'] = f"<a href=\"https://computeruniverse.net/{temp['url']}\">{name}</a>"
            price = row.find_all('div', class_="c-productItem__price--current at__product-price")
            price = price[0].text
            temp['price'] = int(re.findall("\d+", price)[0])
            stock_status = row.find_all('div', class_="c-productItem__price__avail c-productItem__price__avail--11")
            stock_status = stock_status[0].text.strip()
            temp['status'] = 'ok'
            if stock_status == 'Liefertermin hat erhebliche Schwankungen':
                temp['status'] = 'fail'
            if (temp['price'] > 600 and temp['price'] < 900):
                results.append(temp)        
    return results

def cyberport(results):
    r = requests.get('https://www.cyberport.de/tools/search-results.html?autosuggest=false&q=%22geforce+rtx+3080%22')
    if (r.status_code is 200):
        html = BeautifulSoup(r.text, 'html.parser')
        search_results = html.find_all('article')
        for row in search_results:
            temp = {}
            product_link = row.find_all('a', class_="heading-level3")
            product_link = product_link[0]
            temp['shop'] = 'cyberport'
            temp['url'] = product_link.get('href')
            name = row.attrs.get('data-product-name')
            temp['name'] = f"<a href=\"https://cyberport.de/{temp['url']}\">{name}</a>"
            temp['price'] = int(float(row.attrs.get('data-product-price')))
            stock_status = row.find_all('span', class_="tooltipAppend")[0].text.strip()
            temp['status'] = 'fail'
            temp['availability'] = stock_status
            if (stock_status != 'Noch nicht verfügbar'):
                temp['status'] = 'ok'
            if (temp['price'] > 600 and temp['price'] < 900):
                results.append(temp)
    return results


print("\nRTX watch bot running")
while (True):
    result = execute()
    file = open(config['out'], 'w')
    file.write(result)
    file.close()
    time.sleep(config['regenerate'])
