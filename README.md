## Парсер для Cian.ru

cian_parser.py - сам парсер. Считывает ссылки для всех регионов Москвы, /n 
и по всем доступным квартирам находит основную информацию.
И сохраняет итоговый файл Data_cian_full.csv

CMF_CIAN_parser.ipynb - промежуточные вычисления. проверки функций.

Data_cian_full.csv - файл с полученными данными.

## Описание полей данных:
*District* - Район.

	|Цао - 0  
	|САО - 1  
	|СВАО - 2  
	|ВАО - 3  
	|ЮВАО - 4  
	|ЮАО - 5  
	|ЮЗАО - 6  
	|ЗАО - 7  
	|СЗАО - 8  
	|ЗЕЛАО - 9  
	|НАО - 10  
	|ТАО - 11  
	|Price  
	|Tel  
	
*combined_bs* - Количество совмещенных ванных (туалет + ванная комната в одной комнате)  
*cooking_space* - Площадь кухни (м^2)  
*dist* - Дистанция в км от центра города с координатами  

        |37.62209300000001 lon  
        |55.75399399999374 lat  
        
*floor* - Этаж  
*house_type* - тип дома  
*lat, lon* - координаты дома  
*link* - Номер квартиры 

        |ccылку на квартиру можно получить так 'http://www.cian.ru/sale/flat/' + str(link) + '/'  
        
*living_space* - жилая площадь в м^2  
*metro_station* - ближайшая станция метро  
*metro_time* - время за которое можно добраться до метро  
*new* - 1 если новостройка, 2 если вторичка  
*rooms* - количество комнат. если не указано, то их так много, что ты точно не сможешь себе позволить эту квартиру  
*separate_bs* - Количество раздельных сан. узлов  
*total_floors* - общее количество этажей в доме  
*total_space* - Полная площадь квартиры  
*walk* - 1 если до метро пешком, 0 если на транспорте    


Я бы еще добавил информацию по балконам