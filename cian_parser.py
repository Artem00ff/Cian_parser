# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time
import math
import datetime

cy = math.radians(37.62209300000001)
cx = math.radians(55.75399399999374)

def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))
def n_stripper(text):
    return re.sub('\n', '', str(text))
def _stripper(text):
    return re.sub(' ', '', str(text))
def getPrice(flat_page):
    price = flat_page.find('div', attrs={'class':'object_descr_price'})
    price = re.split('<div>|руб|\W', str(price))
    price = "".join([i for i in price if i.isdigit()][-3:])
    return price
def getCoords(flat_page):
    coords = flat_page.find('div', attrs={'class':'map_info_button_extend'}).contents[1]
    coords = re.split('&amp|center=|%2C', str(coords))
    coords_list = []
    for item in coords:
        if item[0].isdigit():
            coords_list.append(item)
    lat = float(coords_list[0])
    lon = float(coords_list[1])
    x = math.radians(lat) #широта
    y = math.radians(lon) #долгота
    distance=6371*math.acos(math.sin(cy)*math.sin(y)+math.cos(cy)*math.cos(y)*math.cos(cx-x))# км
    return lat, lon, distance

def getRoom(flat_page):
    rooms = flat_page.find('div', attrs={'class':'object_descr_title'})
    rooms = html_stripper(rooms)
    room_number = ''
    for i in re.split('-|\n', rooms):
        if 'комн' in i:
            break
        else:
            room_number += i
    room_number = "".join(room_number.split())
    return room_number

def getMetro(flat_page):
    metro = flat_page.find('div', attrs={'class':'object_descr_metro'})
    metro = html_stripper(metro)
    metro = n_stripper(metro)
    if(metro != ''):
        metro_station = re.split(',|мин[.]', metro)[0]
        if(_stripper(re.split(',|мин[.]', metro)[1])!=''):
            if(_stripper(re.split(',|мин[.]', metro)[1]).isdigit()):
                metro_time = int(_stripper(re.split(',|мин[.]', metro)[1]))
            else:
                metro_time = None
            
            if( _stripper(re.split(',|мин[.]', metro)[2])=='пешком'):
                walk=1
            elif(_stripper(re.split(',|мин[.]', metro)[2])=='на машине'):
                walk=0 
            else:
                walk=None
        else:
            metro_time = None
            walk = None
    else:
        metro_time, metro_station, walk = (None,None,None)
    return metro_time, metro_station, walk

def getTable(flat_page):
    table = html_stripper(flat_page.find('table', attrs = {'class':'object_descr_props'}))
    if(len(re.findall('\d+', re.split('Этаж|Тип дома', table)[1]))==2):
        floor, total_floors = re.findall('\d+', re.split('Этаж|Тип дома', table)[1])
        floor = int(floor)
        total_floors = int(total_floors)
    else:
        floor = int(re.findall('\d+', re.split('Этаж|Тип дома', table)[1])[0])
        total_floors = None
        
    if (len(re.split(r',',re.sub(r'\n| ','',re.split('Тип дома:|Тип продажи|Высота потолков:', table)[1])))==2):
        new = re.split(r',',re.sub(r'\n| ','',re.split('Тип дома:|Тип продажи|Высота потолков:', table)[1]))[0]
        house_type = re.split(r',',re.sub(r'\n| ','',re.split('Тип дома:|Тип продажи|Высота потолков:', table)[1]))[1]
    else:
        new = re.split(r',',re.sub(r'\n| ','',re.split('Тип дома:|Тип продажи|Высота потолков:', table)[1]))[0]
        house_type = 'Else'
    if(new=='новостройка'):
        new = 1
    else:
        new = 0
        
    if(re.search( 'Общая площадь:\n\n\xe2\x80\x93', table)):
        total_space = None
    else:
        total_space = re.findall( r'\d+\,*\d*', re.split('Общая площадь:|Площадь кухни:', table)[1] )[0]
        total_space = float(re.sub(',','.',total_space))
            
    #total_space = re.findall( r'\d+\,*\d*', re.split('Общая площадь:|м2', table)[1] )[0]
    if(re.search( 'Жилая площадь:\n\n\xe2\x80\x93', table)):
        living_space = None
    else:
        living_space = re.findall( r'\d+\,*\d*', re.split('Жилая площадь:|Площадь кухни:', table)[1] )[0]
        living_space = float(re.sub(',','.',living_space))
        
    if(re.search(r'Площадь кухни:\n\n\d+\,*\d*', table)):
        cooking_space = re.findall( r'\d+\,*\d*',re.findall( r'Площадь кухни:\n\n\d+\,*\d*', table)[0])[0]
        cooking_space = float(re.sub(',','.',cooking_space))
    else:
        cooking_space = None
        
    if(re.search( 'Совмещенных санузлов:\n\d', table)):
        combined_bs = int(re.search( 'Совмещенных санузлов:\n\d', table).group(0)[-1])
    else:
        combined_bs = 0
        
    if(re.search( 'Раздельных санузлов:\n\d', table)):
        separate_bs = int(re.search( 'Раздельных санузлов:\n\d', table).group(0)[-1])
    else:
        separate_bs = 0
        
    Tel = len(re.findall(r'Телефон:\nда', table))   
        
    return floor, total_floors,new,house_type,total_space,living_space,cooking_space,combined_bs,separate_bs,Tel

def evaluate_flat(link, District=0):
    flat_url = 'http://www.cian.ru/sale/flat/' + str(link) + '/'
    #flat_url = 'http://www.cian.ru/sale/flat/150531912/' 
    flat_page = requests.get(flat_url)
    flat_page = flat_page.content
    flat_page = BeautifulSoup(flat_page, 'lxml')
    flatStats = {'District':District}
    flatStats['link']=link
    flatStats['Price'] = getPrice(flat_page)
    flatStats['lat'], flatStats['lon'],flatStats['dist'] = getCoords(flat_page)
    flatStats['rooms'] = getRoom(flat_page)
    flatStats['floor'], flatStats['total_floors'],flatStats['new'],\
    flatStats['house_type'],flatStats['total_space'],flatStats['living_space'],\
    flatStats['cooking_space'],flatStats['combined_bs'],flatStats['separate_bs'],flatStats['Tel'] = getTable(flat_page)
    flatStats['metro_time'],flatStats['metro_station'],flatStats['walk'] = getMetro(flat_page)
    return flatStats




districts = range(13)
#Цао    
districts[0] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=13&district%5B1%5D=14&district%5B2%5D=15&district%5B3%5D=16&district%5B4%5D=17&district%5B5%5D=18&district%5B6%5D=19&district%5B7%5D=20&district%5B8%5D=21&district%5B9%5D=22&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'    
#САО
districts[1] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=23&district%5B10%5D=33&district%5B11%5D=34&district%5B12%5D=35&district%5B13%5D=36&district%5B14%5D=37&district%5B15%5D=38&district%5B1%5D=24&district%5B2%5D=25&district%5B3%5D=26&district%5B4%5D=27&district%5B5%5D=28&district%5B6%5D=29&district%5B7%5D=30&district%5B8%5D=31&district%5B9%5D=32&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#СВАО
districts[2] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=39&district%5B10%5D=49&district%5B11%5D=50&district%5B12%5D=51&district%5B13%5D=52&district%5B14%5D=53&district%5B15%5D=54&district%5B16%5D=55&district%5B1%5D=40&district%5B2%5D=41&district%5B3%5D=42&district%5B4%5D=43&district%5B5%5D=44&district%5B6%5D=45&district%5B7%5D=46&district%5B8%5D=47&district%5B9%5D=48&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ВАО
districts[3] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=56&district%5B10%5D=66&district%5B11%5D=67&district%5B12%5D=68&district%5B13%5D=69&district%5B14%5D=70&district%5B15%5D=71&district%5B1%5D=57&district%5B2%5D=58&district%5B3%5D=59&district%5B4%5D=60&district%5B5%5D=61&district%5B6%5D=62&district%5B7%5D=63&district%5B8%5D=64&district%5B9%5D=65&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЮВАО
districts[4] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=72&district%5B10%5D=82&district%5B11%5D=83&district%5B1%5D=73&district%5B2%5D=74&district%5B3%5D=75&district%5B4%5D=76&district%5B5%5D=77&district%5B6%5D=78&district%5B7%5D=79&district%5B8%5D=80&district%5B9%5D=81&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЮАО
districts[5] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=84&district%5B10%5D=94&district%5B11%5D=95&district%5B12%5D=96&district%5B13%5D=97&district%5B14%5D=98&district%5B15%5D=99&district%5B1%5D=85&district%5B2%5D=86&district%5B3%5D=87&district%5B4%5D=88&district%5B5%5D=89&district%5B6%5D=90&district%5B7%5D=91&district%5B8%5D=92&district%5B9%5D=93&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЮЗАО
districts[6] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=100&district%5B10%5D=110&district%5B11%5D=111&district%5B1%5D=101&district%5B2%5D=102&district%5B3%5D=103&district%5B4%5D=104&district%5B5%5D=105&district%5B6%5D=106&district%5B7%5D=107&district%5B8%5D=108&district%5B9%5D=109&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЗАО
districts[7] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=112&district%5B10%5D=122&district%5B11%5D=123&district%5B12%5D=124&district%5B13%5D=348&district%5B14%5D=349&district%5B15%5D=350&district%5B1%5D=113&district%5B2%5D=114&district%5B3%5D=115&district%5B4%5D=116&district%5B5%5D=117&district%5B6%5D=118&district%5B7%5D=119&district%5B8%5D=120&district%5B9%5D=121&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#СЗАО
districts[8] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=125&district%5B1%5D=126&district%5B2%5D=127&district%5B3%5D=128&district%5B4%5D=129&district%5B5%5D=130&district%5B6%5D=131&district%5B7%5D=132&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЗЕЛАО
districts[9] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=152&district%5B1%5D=153&district%5B2%5D=154&district%5B3%5D=355&district%5B4%5D=356&district%5B5%5D=357&district%5B6%5D=358&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#НАО
districts[10] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=327&district%5B10%5D=337&district%5B1%5D=328&district%5B2%5D=329&district%5B3%5D=330&district%5B4%5D=331&district%5B5%5D=332&district%5B6%5D=333&district%5B7%5D=334&district%5B8%5D=335&district%5B9%5D=336&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ТАО
districts[11] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=338&district%5B1%5D=339&district%5B2%5D=340&district%5B3%5D=341&district%5B4%5D=342&district%5B5%5D=343&district%5B6%5D=344&district%5B7%5D=345&district%5B8%5D=346&district%5B9%5D=347&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'

Data = pd.DataFrame()
start_time = datetime.datetime.now()
for district_num in range(12):
    links = []
    for page in range(1, 30):
        page_url =  districts[district_num].format(page)
        
        search_page = requests.get(page_url)
        search_page = search_page.content
        search_page = BeautifulSoup(search_page, 'lxml')
        
        flat_urls = search_page.findAll('div', attrs = {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
        flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))
        #if(flat_urls[1] in links): break
        for link in flat_urls:
            if link.isdigit():
                if(link in links):
                    break
                else:
                    links.append(link)  
                
    print('Start parse district %d, %d links in it'% (district_num,len(links),))    
    
    
    for link in links:
        #last_link=link
        stats = evaluate_flat(link,District= district_num)
        TempData = pd.DataFrame.from_records([stats])
        Data = Data.append(TempData, ignore_index=True)
    print('District %d done'%(district_num,))

print('Total time  ' + str(datetime.datetime.now() - start_time))

Data.to_csv('Data_cian_full.csv')

Data['Price'] = Data['Price'].apply(lambda x: int(x))
 
Data.to_csv('Data_cian_full.csv')        
    
    
    
    
    
    
    
    
    
    
    
