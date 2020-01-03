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
from datetime import timedelta, datetime, date, time
import requests
import dataset
import hashlib

db = dataset.connect('mysql://django:cxzaq15061999@localhost/iiko')

def isLogin(server, login, password):
    try:
        url = "http://"+str(server)+":8080/resto/api/auth?login="+str(login)+ "&pass="+ str(password)
        token = requests.get(url).text
        #print(url)
        #print(token)
    except Exception:
        return '0'
    if len(token.split('-')[0]) != 8:
        return '0'
    return str(token)

def isLoginBiz(login,password):
    try:
        url = "https://iiko.biz:9900/api/0/auth/access_token?user_id="+login+"&user_secret="+password
        token = requests.get(url).text
        token = token[1:len(token)-1]
        print(len(token))
        #print(url)
        print(token)
    except Exception:
        return '0'
    if len(token) != 87:
        return '0'
    return str(token)

def datadelta():
    now = datetime.now()
    change_pyt = now.weekday() - 4
    #print(change_pyt)
    if change_pyt<0:
        change_pyt+=7
    #print(change_pyt)
    del_days = timedelta(change_pyt)
    #print(del_days)
    now = now -del_days
    #print(now)                            
    seven_days = timedelta(7)  
    to_seven_days = now - seven_days
    now_str = str(now.year)+'-'
    str_seven_days = str(to_seven_days.year)+'-'
    if now.month<10:
    	now_str=now_str+"0"
    	print(now_str)
    if to_seven_days.month<10:
    	str_seven_days=str_seven_days+"0"
    now_str = now_str+str(now.month) + '-'
    str_seven_days = str_seven_days +str(to_seven_days.month) + '-'
    if now.day<10:
    	now_str=now_str+"0"
    if to_seven_days.day<10:
    	str_seven_days=str_seven_days+"0"
    now_str=now_str+str(now.day)
    str_seven_days=str_seven_days+str(to_seven_days.day)
    print(str_seven_days)
    print(now_str)
    return [now_str, str_seven_days, now, to_seven_days]   

def get_info_iiko(server_name):
    now = datetime.now()               
    seven_days = timedelta(7)
    to_seven_days = now - seven_days
    now_str = str(now.day)+'.'+str(now.month) + '.'+ str(now.year)
    str_seven_days = str(to_seven_days.day)+'.'+str(to_seven_days.month) + '.'+str(to_seven_days.year)
    deltadata = [now_str,str_seven_days]
    #print(deltadata)
    table = db['user']
    row = table.find_one(id=server_name)
    url_zapr = 'http://'+str(server_name)+':8080/resto/api/reports/olap?key='+str(row['token'])+'&report=SALES&from='+str(deltadata[1])+'&to='+str(deltadata[0])+'&agr=fullSum&agr=OrderNum&agr=ProductCostBase.ProductCost&agr=DishAmountInt&agr=GuestNum.Avg&groupRow=Delivery.IsDelivery&agr=DishDiscountSumInt.averagePrice'
    text_zapr= requests.get(url_zapr, headers={'Content-Type':'text/xml'}).text
    #print(text_zapr)
    if text_zapr == 'Token is expired or invalid':
        token = isLogin(server_name,str(row['login']),str(row['pass']))
        data_token = dict(id=server_name, token=token)
        table.update(data_token, ['id'])
        url_zapr = 'http://'+str(server_name)+':8080/resto/api/reports/olap?key='+str(row['token'])+'&report=SALES&from='+deltadata[1]+'&to='+deltadata[0]+'&agr=fullSum&agr=OrderNum&agr=ProductCostBase.ProductCost&agr=DishAmountInt&agr=GuestNum.Avg&groupRow=Delivery.IsDelivery&agr=DishDiscountSumInt.averagePrice'
        text_zapr= requests.get(url_zapr, headers={'Content-Type':'text/xml'}).text

    xml_parse = xmltodict.parse(text_zapr)
    AGPrice = xml_parse['report']['r']['DishDiscountSumInt.averagePrice']
    AGCount = float(xml_parse['report']['r']['DishAmountInt'])*1.0 / float(xml_parse['report']['r']['OrderNum'])
    NetCost = float(xml_parse['report']['r']['ProductCostBase.ProductCost']) *1.0 / float(xml_parse['report']['r']['OrderNum'])
    return [float(AGPrice), float(AGCount),float(NetCost)]


def calc(server_name):

  deltadata = datadelta()
  table = db['user']
  row = table.find_one(id=server_name)
  print("sdfds")
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


def combo_skidka(server_name, date1,date2):
    deltadata = datadelta()
    table = db['user']
    row = table.find_one(id=server_name)
    url_abc = 'http://'+str(server_name)+':8080/resto/api/v2/reports/olap?&key='+str(row['token'])
    data = {
      "reportType": "SALES",
      "groupByRowFields": [],
      "groupByColFields": [],
      "aggregateFields": [
        "ItemSaleEventDiscountType.ComboAmount"
      ],
      "filters": {
        "OpenDate.Typed": {
          "filterType": "DateRange",
          "periodType": "CUSTOM",
          "from": date2 + "T00:00:00.000",
          "to": date1 + "T00:00:00.000",
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
    return int(text_abc.json()['data'][0]['ItemSaleEventDiscountType.ComboAmount'])

def convers_user2(server_name, date1,date2,date_p1,date_p2):
	#deltadata = datadelta()
	table = db['user']
	row = table.find_one(id=server_name)
	url_abc = 'http://'+str(server_name)+':8080/resto/api/v2/reports/olap?&key='+str(row['token'])
	data = {
		"reportType": "SALES",
		"groupByRowFields": [],
		"groupByColFields": ["Delivery.CustomerCardNumber","Delivery.CustomerCreatedDateTyped"],
		"aggregateFields": [
		"GuestNum"
	],
	"filters": {
		"OpenDate.Typed": {
		"filterType": "DateRange",
		"periodType": "CUSTOM",
		"from": date2 + "T00:00:00.000",
		"to": date1 + "T00:00:00.000",
		"includeLow": 'true',
		"includeHigh": 'false'
		}
	}
	}
    
	text_abc = requests.post(url_abc, json = data)
	#print(text_abc.text)
	if text_abc.text == 'Token is expired or invalid':
		token = isLogin(server_name,str(row['login']),str(row['pass']))
		data_token = dict(id=server_name, token=token)
		table.update(data_token, ['id'])
		url_abc = 'http://'+str(server_name)+':8080/resto/api/v2/reports/olap?&key='+str(token)
		text_abc = requests.post(url_abc, json = data)
	#print(text_abc.json())
	summa_avc = 0
	vol_guestc= 0
	all_guestc = 0
	now = date_p1
	to_seven_days = date_p2
	for guest in text_abc.json()['data']:
		if (guest['Delivery.CustomerCardNumber'] != None):
			data_sozd = guest['Delivery.CustomerCreatedDateTyped']
			data_sozd  = datetime.strptime(data_sozd+"-12:30","%Y-%m-%d-%I:%M")
			if (data_sozd<now) and (data_sozd>to_seven_days):
				print(guest)
				summa_avc = summa_avc + guest['GuestNum']
				all_guestc +=1
				if guest['GuestNum']!=0:
					vol_guestc+=1
	return [all_guestc,vol_guestc,summa_avc]


def client(server_name, date1,date2,date_p1,date_p2):
	#deltadata = datadelta()
	table = db['user']
	row = table.find_one(id=server_name)
	url_abc = 'http://'+str(server_name)+':8080/resto/api/v2/reports/olap?&key='+str(row['token'])
	data = {
		"reportType": "SALES",
		"groupByRowFields": [],
		"groupByColFields": ["Delivery.CustomerCardNumber","Delivery.CustomerCreatedDateTyped"],
		"aggregateFields": [
		"GuestNum"
	],
	"filters": {
		"OpenDate.Typed": {
		"filterType": "DateRange",
		"periodType": "CUSTOM",
		"from": date2 + "T00:00:00.000",
		"to": date1 + "T00:00:00.000",
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
	#print(text_abc.json())
	clients = 0
	now = date_p2+timedelta(7)
	to_seven_days = date_p2
	for guest in text_abc.json()['data']:
		print(to_seven_days)
		if (guest['Delivery.CustomerCardNumber'] != None):
			data_sozd = guest['Delivery.CustomerCreatedDateTyped']
			data_sozd  = datetime.strptime(data_sozd+"-12:30","%Y-%m-%d-%I:%M")
			print(guest)
			if (data_sozd<now) and (data_sozd>to_seven_days):
				if guest['GuestNum']>1:
					clients+=1
	return clients




def convers_user(server_name, date1,date2):
    table = db['user']
    row = table.find_one(id=server_name)
    token  = row['token_biz']
    r = requests.get("https://iiko.biz:9900/api/0/organization/list?access_token="+token).text
    print(r.split(",")[0])
    if r.split(",")[0] =='{"code":null':
        print("DSFs")
        token = isLoginBiz(row['login_biz'],row['pass_biz'])
        print(token)
        r = requests.get("https://iiko.biz:9900/api/0/organization/list?access_token="+token).text
        data = dict(id=server_name, token_biz=token)
        table.update(data, ['id'])
    organisation_id = json.loads(r)[0]['id']
    deltadata = datadelta()
    
    url_P = ("https://iiko.biz:9900/api/0/customers/get_customers_by_organization_and_by_period?access_token="+token+"&organization="+organisation_id+"&dateFrom="+str(deltadata[1])+"&dateTo="+str(deltadata[0]))
    print(url_P)
    r = requests.get(url_P)
    print("________________________")
    print(r.text)

    infor_abc =  r.json()
    now = deltadata[2]
    to_seven_days = deltadata[3]
    t2 = 0
    t = 0   
    for i in infor_abc:
      p  = datetime.strptime(i["whenCreated"].split("T")[0]+"-12:30","%Y-%m-%d-%I:%M")
      print(i)
      if (now>p) and (p>to_seven_days):
          t2+=1
          try:
            p2  = datetime.strptime(i["lastVisitDate"].split("T")[0]+"-12:30","%Y-%m-%d-%I:%M")
            if (now>p2) and (p2>to_seven_days):
                print(i["phone"], i["lastVisitDate"])
                t+=1
          except Exception:
            print("__")
    return [t,t2,str(deltadata[0])]




def unit_calc(server_name, Other=50,AC = 2000, RC = 2000):
    now, seven_days, now_p, seven_days_p = datadelta()
    print(now)
    print(seven_days)
    AGPrice,AGCount,NetCost = get_info_iiko(server_name)
    #user_buy, user_all, date = convers_user(server_name)
    #user_combo=combo_skidka(server_name)
    user_all, user_buy, vol_avc= convers_user2(server_name,now,seven_days,now_p, seven_days_p)
    table = db[str(server_name)]
    buyers = user_buy
    UA = user_all #Число подписчиков чатбота, которые конвертируются в покупателей
    try:
        C1 = user_buy*1.0/user_all  #Конверсия подписчиков чатбота в Покупателей в
    except ZeroDivisionError:
        C1 = 0
    AVPrice = AGPrice * AGCount #Средний чек в магазине
    
    try:
        APC = vol_avc*1.0/buyers #Затраты на привлечение одного подписчика, установившего чатбота
    except ZeroDivisionError:
        APC = 0
     #Среднее число приходов (в когорте) одним Покупателем, установившем чатбота
    Delivery = 0 #= fdata[server_name]['Delivery']
    ARPPU = (AVPrice - (NetCost + Delivery + Other)) * APC #Доход с одного платящего клиента за время жизни когорты.
    
    ARPU = ARPPU *1.0 * C1 #Доход с одного уникального подписчика чатбота
    
    #Бюджет на привлечение когорты: десерт покупателю + 50 руб за каждую установку - продавцу
    try:
        CPA = AC / UA #Затраты на привлечение одного подписчика, установившего чатбота
    except ZeroDivisionError:
        CPA = 0
    #Бюджет на удержание клиентов: бонусы, персонализация, привилегии
    try:
        ARC = RC * C1 / buyers #Средние затраты на удержание подписчика чат-бота
    except ZeroDivisionError:
        ARC = 0
    ARPU_CPA_ARC = ARPU - CPA - ARC #Прибыль с одного уникального подписчика чатбота
    Revenue = ARPU_CPA_ARC * UA #Прибыль,  которую мы получаем в когорте.
    ROI = (ARPPU * buyers - (AC + RC))/(AC + RC) * 100#ROI
    #table.insert({'date': date, 'new_client':str(user_buy), 'new_client_to2':'0', 'vol_par':'0','cost_uder':str(ARC),'cost_priv':str(CPA), 'prib_1people':str(ARPU_CPA_ARC),'prib_kogort':str(Revenue)})
    row = table.find_one(date="2019-11-29")
    print(row)
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
            data = dict(id=server, token=token)
            table.update(data, ['id'])
            request.session['server'] = str(server)
            print(request.session['server'])
            return redirect('/plat')

def regin(request):
    if request.method == 'POST':
        server = str(request.POST['server'])
        login = request.POST['login']
        password = hex(request.POST['pass'])
        print(request.POST)
        login_iiko = request.POST['login_biz']
        pass_iiko = request.POST['pass_biz']
        token2 = isLoginBiz(login_iiko,pass_iiko)
        token = isLogin(server, login, password)
        print(token)
        print(token2)
        if token == '0':
            return redirect('/reg')
        elif token2 == '0':
            return redirect('/reg')
        else:
            table = db['user']
            row = table.find_one(id=server) 
            if row == None:
                table.insert({'id':server, 'login':login, 'token':token, 'pass':password, 'token_biz':token2, 'login_biz':login_iiko, 'pass_biz':pass_iiko})
                table3 = db.create_table(server,
                         primary_id='date',
                         primary_type=db.types.string(35))
                table3.create_column('new_client', db.types.text)
                table3.create_column('new_client_to2', db.types.text)
                table3.create_column('vol_par', db.types.text)
                table3.create_column('cost_uder', db.types.text)
                table3.create_column('cost_priv', db.types.text)
                table3.create_column('prib_1people', db.types.text)
                table3.create_column('prib_kogort', db.types.text)
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

def reg(request):
    return render(request, 'index_login2.html')\

def graf(request):
    return render(request, 'index_graf.html')


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

def graf_p(request):
	print(request.session['server'])
	now, seven_days, now_p, seven_days_p = datadelta()
	array = []
	vol1=[]
	vol1.append(['Дата','Количество покупателей'])
	#print([i for i in range(10, 1, -1)])
	for i in range(10,0,-1):
		del_seven_days = now_p-timedelta(7*i)
		del2_seven_days = now_p-timedelta(7*(i-1))
		now_str = str(del2_seven_days.year)+'-'
		str_seven_days = str(del_seven_days.year)+'-'
		if del2_seven_days.month<10:
			now_str=now_str+"0"
		if del_seven_days.month<10:
			str_seven_days=str_seven_days+"0"
		now_str = now_str+str(del2_seven_days.month) + '-'
		str_seven_days = str_seven_days +str(del_seven_days.month) + '-'


		#now_str = str(del2_seven_days.year)+'-'+str(del2_seven_days.month) + '-'
		#str_seven_days = str(del_seven_days.year)+'-'+str(del_seven_days.month) + '-'

		if del2_seven_days.day<10:
			now_str=now_str+"0"
		if del_seven_days.day<10:
			str_seven_days=str_seven_days+"0"
		now_str=now_str+str(del2_seven_days.day)
		str_seven_days=str_seven_days+str(del_seven_days.day)
		#print([now_str,str_seven_days])
		vol_guests = convers_user2(request.session['server'],now_str,str_seven_days,del2_seven_days,del_seven_days)[1]
		vol1.append([now_str, vol_guests])
	print(vol1)
	array.append(vol1)
	vol1=[]
	vol1.append(['Дата','Количество проданнх офферов'])
	print([i for i in range(8, 0, -1)])
	for i in range(10,0,-1):
		del_seven_days = now_p-timedelta(7*i)
		del2_seven_days = now_p-timedelta(7*(i-1))


		now_str = str(del2_seven_days.year)+'-'
		str_seven_days = str(del_seven_days.year)+'-'
		if del2_seven_days.month<10:
			now_str=now_str+"0"
		if del_seven_days.month<10:
			str_seven_days=str_seven_days+"0"
		now_str = now_str+str(del2_seven_days.month) + '-'
		str_seven_days = str_seven_days +str(del_seven_days.month) + '-'

		#now_str = str(del2_seven_days.year)+'-'+str(del2_seven_days.month) + '-'
		#str_seven_days = str(del_seven_days.year)+'-'+str(del_seven_days.month) + '-'

		if del2_seven_days.day<10:
			now_str=now_str+"0"
		if del_seven_days.day<10:
			str_seven_days=str_seven_days+"0"
		now_str=now_str+str(del2_seven_days.day)
		str_seven_days=str_seven_days+str(del_seven_days.day)
		#print([now_str,str_seven_days])
		vol_guests = combo_skidka(request.session['server'],now_str,str_seven_days)
		vol1.append([now_str, vol_guests])
	print(vol1)
	array.append(vol1)
	vol1=[]
	vol1.append(['Дата','Количество клиентов'])
	#print([i for i in range(8, 1, -1)])
	for i in range(10,0,-1):
		del_seven_days = now_p-timedelta(7*i)
		del2_seven_days = now_p
		del3_seven_days = del_seven_days + timedelta(7)
		now_str = str(del2_seven_days.year)+'-'
		str_seven_days = str(del_seven_days.year)+'-'
		str2_seven_days = str(del3_seven_days.year)+'-'
		if del2_seven_days.month<10:
			now_str=now_str+"0"
		if del_seven_days.month<10:
			str_seven_days=str_seven_days+"0"
		if del3_seven_days.month<10:
			str2_seven_days=str2_seven_days+"0"
		now_str = now_str+str(del2_seven_days.month) + '-'
		str_seven_days = str_seven_days +str(del_seven_days.month) + '-'
		str2_seven_days = str2_seven_days +str(del3_seven_days.month) + '-'

		#now_str = str(del2_seven_days.year)+'-'+str(del2_seven_days.month) + '-'
		#str_seven_days = str(del_seven_days.year)+'-'+str(del_seven_days.month) + '-'


		if del2_seven_days.day<10:
			now_str=now_str+"0"
		if del_seven_days.day<10:
			str_seven_days=str_seven_days+"0"
		if del3_seven_days.day<10:
			str2_seven_days=str2_seven_days+"0"

		now_str=now_str+str(del2_seven_days.day)
		str_seven_days=str_seven_days+str(del_seven_days.day)
		str2_seven_days=str2_seven_days+str(del3_seven_days.day)
		#print([now_str,str_seven_days])
		vol_guests = client(request.session['server'],now_str,str_seven_days,del2_seven_days,del_seven_days)
		vol1.append([str2_seven_days, vol_guests])
	#print(vol1)
	array.append(vol1)
	return HttpResponse(json.dumps(array), content_type="application/json")
