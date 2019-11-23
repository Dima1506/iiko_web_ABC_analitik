from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
import re
from django.conf import settings
from django.conf.urls.static import static
import json
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import xmltodict, json
from datetime import timedelta, datetime
import requests
import dataset
import hashlib

db = dataset.connect('mysql://django:cxzaq15061999@localhost/iiko')

def isLogin(server, login, password):
    try:
        url = "http://"+str(server)+":8080/resto/api/auth?login="+str(login)+ "&pass="+ str(password)
        token = requests.get(url).text
        print(url)
        print(token)
    except Exception:
        return '0'
    if len(token.split('-')[0]) != 8:
        return '0'
    return str(token)

def datadelta():
    now = datetime.now()               
    seven_days = timedelta(7)
    to_seven_days = now - seven_days
    now_str = str(now.year)+'-'+str(now.month) + '-'
    str_seven_days = str(to_seven_days.year)+'-'+str(to_seven_days.month) + '-'
    if now.day<10:
    	now_str=now_str+"0"
    if to_seven_days.day<10:
    	str_seven_days=str_seven_days+"0"
    now_str=now_str+str(now.day)
    str_seven_days=str_seven_days+str(to_seven_days.day)
    return [now_str, str_seven_days]   

def get_info_iiko(server_name):
    now = datetime.now()               
    seven_days = timedelta(7)
    to_seven_days = now - seven_days
    now_str = str(now.day)+'.'+str(now.month) + '.'+ str(now.year)
    str_seven_days = str(to_seven_days.day)+'.'+str(to_seven_days.month) + '.'+str(to_seven_days.year)
    now_str2 = str(now.year) +'-'+str(now.month)+'-'+str(now.day) 
    str_seven_days2 = str(to_seven_days.year) +'-'+str(to_seven_days.month)+'-'+str(to_seven_days.day) 
    deltadata = [now_str,str_seven_days]
    print(deltadata)
    table = db['user']
    row = table.find_one(id=server_name)
    url_zapr = 'http://'+str(server_name)+':8080/resto/api/reports/olap?key='+str(row['token'])+'&report=SALES&from='+str(deltadata[1])+'&to='+str(deltadata[0])+'&agr=fullSum&agr=OrderNum&agr=ProductCostBase.ProductCost&agr=DishAmountInt&agr=GuestNum.Avg&groupRow=Delivery.IsDelivery&agr=DishDiscountSumInt.averagePrice'
    text_zapr= requests.get(url_zapr, headers={'Content-Type':'text/xml'}).text
    print(text_zapr)
    if text_zapr == 'Token is expired or invalid':
        token = isLogin(server_name,str(row['login']),str(row['pass']))
        data_token = dict(id=server_name, token=token)
        table.update(data_token, ['id'])
        url_zapr = 'http://'+str(server_name)+':8080/resto/api/reports/olap?key='+str(row['token'])+'&report=SALES&from='+deltadata[1]+'&to='+deltadata[0]+'&agr=fullSum&agr=OrderNum&agr=ProductCostBase.ProductCost&agr=DishAmountInt&agr=GuestNum.Avg&groupRow=Delivery.IsDelivery&agr=DishDiscountSumInt.averagePrice'
        text_zapr= requests.get(url_zapr, headers={'Content-Type':'text/xml'}).text

    url_get_user = "http://aleksandra-ip-sergaev.iiko.it:8080/resto/api/v2/reports/olap?&key="+str(row['token'])
    data_len_user = {
      "reportType": "SALES",
      "groupByColFields": [],
      "aggregateFields": [
        "fullSum"
      ],
      "groupByRowFields":["Delivery.CustomerCardNumber"],
      "filters": {
        "OpenDate.Typed": {
          "filterType": "DateRange",
          "periodType": "CUSTOM",
          "from": str(str_seven_days2) + "T00:00:00.000",
          "to": str(now_str2) + "T00:00:00.000",
          "includeLow": 'true',
          "includeHigh": 'false'
        }
      }
    }
    
    result_user_len = requests.post(url_get_user, json = data_len_user)
    result_user_len = len(result_user_len.json()['data'])-1

    xml_parse = xmltodict.parse(text_zapr)
    AGPrice = xml_parse['report']['r']['DishDiscountSumInt.averagePrice']
    AGCount = float(xml_parse['report']['r']['DishAmountInt'])*1.0 / float(xml_parse['report']['r']['OrderNum'])
    NetCost = float(xml_parse['report']['r']['ProductCostBase.ProductCost']) *1.0 / float(xml_parse['report']['r']['OrderNum'])
    data_unit = dict(id=server_name, AGPrice=AGPrice,AGCount=AGCount, NetCost = NetCost)
    table.update(data_unit, ['id'])


def calc(server_name):
  deltadata = datadelta()
  table = db['user']
  row = table.find_one(id=server_name)
  url_abc = 'http://'+str(server_name)+':8080/resto/api/v2/reports/olap?&key='+str(row['token'])
  data = {
    "reportType": "SALES",
    "groupByRowFields": [],
    "groupByColFields": ['DishName'],
    "aggregateFields": [
      "DishAmountInt",
      "ProductCostBase.ProductCost",
      "fullSum",
      "DishSumInt.averagePriceWithVAT"
    ],
    "filters": {
      "OpenDate.Typed": {
        "filterType": "DateRange",
        "periodType": "CUSTOM",
        "from": str(deltadata[1]) + "T00:00:00.000",
        "to": str(deltadata[0]) + "T00:00:00.000",
        "includeLow": 'true',
        "includeHigh": 'false'
      }
    }
  }
  

  text_abc = requests.post(url_abc, json = data)
  if text_abc.text == 'Token is expired or invalid':
    token = isLogin(server_name,str(row['login']),str(row['pass']))
    data_token = dict(id=server_name, token=token)
    table.update(data_token, ['id'])
    url_abc = 'http://'+str(server_name)+':8080/resto/api/v2/reports/olap?&key='+str(token)
    text_abc = requests.post(url_abc, json = data)
  infor_abc =  text_abc.json()

  tech_p = {}

  summa = {'marsa':0, 'vol':0}
  
  for ip in infor_abc['summary']:
    #tech_p[ip]
    try:
      #print(summa['marsa'])
      #print(str(ip[0]['DishName']) + ' ' + str(ip[1]['fullSum']) + ' ' + str(ip[1]['ProductCostBase.ProductCost'])+ ' ' + str(ip[1]['DishAmountInt']))
      if (ip[1]['fullSum'] >ip[1]['ProductCostBase.ProductCost']) and (ip[1]['ProductCostBase.ProductCost'] != 0) and (ip[1]['fullSum'] != 0):
        t = ip[1]['fullSum'] - ip[1]['ProductCostBase.ProductCost']
        tech_p[ip[0]['DishName']] = [ip[1]['fullSum'] - ip[1]['ProductCostBase.ProductCost'], ((ip[1]['fullSum'] - ip[1]['ProductCostBase.ProductCost'])*100.0/ip[1]['fullSum']),ip[1]['DishAmountInt'], ip[1]['DishSumInt.averagePriceWithVAT']]
        summa['marsa'] = t + summa['marsa']
        summa['vol'] += ip[1]['DishAmountInt']
    except:
      i = 1
      #print("lol")
      #tech_p['NotInfo'] = [ip[1]['fullSum'] - ip[1]['ProductCostBase.ProductCost'], ((ip[1]['fullSum'] - ip[1]['ProductCostBase.ProductCost'])*100.0/ip[1]['fullSum']),ip[1]['DishAmountInt']]
  


  list_d = list(tech_p.items())
  list_d.sort(reverse = True, key=lambda i: i[1][0])
  sum = 0
  for element_mas in list_d:
    p = tech_p[element_mas[0]]
    sum = sum + p[0]

    if sum < summa['marsa']*0.8:
      p.append('A')
    elif sum < summa['marsa']*0.95:
      p.append('B')
    else:
      p.append('C')
    tech_p[element_mas[0]] = p
  #print(list_d)

  list_d.sort(reverse = True, key=lambda i: i[1][1])
  #print(range(len(list_d)))
  for num in range(len(list_d)):
    p = tech_p[list_d[num][0]]
    if num < len(list_d)*0.2:
      p.append('A')
    elif num < len(list_d)*0.5:
      p.append('B')
    else:
      p.append('C')
    tech_p[element_mas[0]] = p

  list_d.sort(reverse = True, key=lambda i: i[1][2])
  sum = 0
  for element_mas in list_d:
    p = tech_p[element_mas[0]]
    sum = sum + p[2]

    if sum < summa['vol']*0.8:
      p.append('A')
    elif sum < summa['vol']*0.95:
      p.append('B')
    else:
      p.append('C')
    tech_p[element_mas[0]] = p
  lines = []
  lines2 = []
  lines3 = []
  lines4 = []
  for ip in tech_p:
    if (tech_p[ip][4]=='A' and tech_p[ip][5]=='A') or (tech_p[ip][4]=='B' and tech_p[ip][5]=='A') :
      lines.append(ip)
      lines3.append(float(tech_p[ip][3]))
      #print('Паровоз '+ip + ' : ' + str(tech_p[ip]))
    if (tech_p[ip][4]=='C' and tech_p[ip][5]=='A' and tech_p[ip][6]=='B') or (tech_p[ip][4]=='C' and tech_p[ip][5]=='A' and tech_p[ip][6]=='C') :
      lines2.append(ip)
      lines4.append(float(tech_p[ip][3]))
      #print('Прицеп '+ip + ' : ' + str(tech_p[ip]))
    if (tech_p[ip][4]=='C' and tech_p[ip][5]=='B' and tech_p[ip][6]=='B') or (tech_p[ip][4]=='C' and tech_p[ip][5]=='B' and tech_p[ip][6]=='C') :
      lines2.append(ip)
      lines4.append(float(tech_p[ip][3]))
      #print('Прицеп '+ip + ' : ' + str(tech_p[ip])
  return [lines, lines2, lines3,lines4]




def unit_calc(server_name, Other=50,AC = 2000, RC = 2000):
    
    get_info_iiko(server_name)
    
    table = db['user']
    row = table.find_one(id=server_name)


    UA = 5000 #Число подписчиков чатбота, которые конвертируются в покупателей
    C1 = 0.2 #Конверсия подписчиков чатбота в Покупателей в
    buyers = UA * C1 #Количество покупателей, с чатботом
    AGPrice = float(row['AGPrice']) #Средняя цена товара в магазине, который покупается клиентами
    AGCount = float(row['AGCount'])#Среднее число товаров в корзине клиента
    AVPrice = AGPrice * AGCount #Средний чек в магазине
    
    NetCost = float(row['NetCost'])#COGS себестоимость
    APC = 5 #Среднее число приходов (в когорте) одним Покупателем, установившем чатбота
    Delivery = 0 #= fdata[server_name]['Delivery']
    ARPPU = (AVPrice - (NetCost + Delivery + Other)) * APC #Доход с одного платящего клиента за время жизни когорты.
    
    ARPU = ARPPU *1.0 * C1 #Доход с одного уникального подписчика чатбота
    
    #Бюджет на привлечение когорты: десерт покупателю + 50 руб за каждую установку - продавцу
    CPA = AC / UA #Затраты на привлечение одного подписчика, установившего чатбота
    #Бюджет на удержание клиентов: бонусы, персонализация, привилегии
    ARC = RC * C1 / buyers #Средние затраты на удержание подписчика чат-бота
    ARPU_CPA_ARC = ARPU - CPA - ARC #Прибыль с одного уникального подписчика чатбота
    Revenue = ARPU_CPA_ARC * UA #Прибыль,  которую мы получаем в когорте.
    ROI = (ARPPU * buyers - (AC + RC))/(AC + RC) * 100#ROI
    return [CPA, ARC, ARPU_CPA_ARC, Revenue, ROI]


def hex(password):
    m = hashlib.md5()
    ps = str(password).encode('utf-8')
    hex_t = hashlib.sha1(ps).hexdigest()
    return str(hex_t)


def signin(request):
    if request.method == 'POST':
        server = str(request.POST['server'])
        login = request.POST['login']
        password = hex(request.POST['pass'])
        token = isLogin(server, login, password)
        if token == '0':
            return redirect('/login')
        else:
            table = db['user']
            row = table.find_one(id=server) 
            if row == None:
                table.insert({'id':server, 'login':login, 'token':token, 'pass':password, 'AGPrice':0, 'NetCost':0, 'AGCount':0})
            data = dict(id=server, token=token)
            table.update(data, ['id'])
            request.session['server'] = str(server)
            print(request.session['server'])
            return redirect('/plat')


def index(request):
    try:
        print(request.session['server'])
        abc_analize = calc(request.session['server'])
        return render(request, 'index.html',{'lines':abc_analize[0],'lines2':abc_analize[1], 'cost1':abc_analize[2], 'cost2':abc_analize[3], 'state':str(request.session['server'])})
    except Exception:
        return render(request, 'index_login.html')


def index_login(request):
    return render(request, 'index_login.html')

def post(request):
    params_for_unit = str(request).split("%3D")
    print(params_for_unit)
    unit_analize = unit_calc(params_for_unit[1].split('&')[0], int(params_for_unit[2].split('&')[0]), int(params_for_unit[3].split('&')[0]),int(params_for_unit[4].split("'>")[0]))
    print(unit_analize)
    return HttpResponse(str(unit_analize))

def bot_info(request):
    file = open('data.txt', 'r')
    data = eval(file.read())
    file.close()
    print(request.POST)