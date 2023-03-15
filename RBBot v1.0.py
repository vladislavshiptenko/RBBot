#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api 
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests 
import json 
import random
from array import *
from bs4 import BeautifulSoup

random_id = random.randint(100000000, 999999999)
ID = array('i', [100000000])
d = {}
token = "*some token*"

keyboard1 = VkKeyboard(one_time=True)
keyboard1.add_button('Хочу приобрести товар', color=VkKeyboardColor.POSITIVE)
keyboard1.add_line()
keyboard1.add_button('Хочу продать товар', color=VkKeyboardColor.PRIMARY)

keyboard2 = VkKeyboard(one_time=True)
keyboard2.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

def write_msg_before(user_id, message):
	global msg
	vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id':random_id, 'keyboard':keyboard1.get_keyboard()})

def write_msg_after(user_id, message):
	global msg
	vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id':random_id, 'keyboard':keyboard2.get_keyboard()})

def write_msg_cat(user_id, message):
	global msg
	vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id':random_id, 'keyboard':keyboard3.get_keyboard()})

def write_json(data): 
	with open(str(user_id), 'w') as file: 
		json.dump(data, file, indent = 2, ensure_ascii = False) 

def write_json_normal(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent = 2, ensure_ascii = False)

def info(): 
	i = 'nom'
	r = requests.get('https://api.vk.com/method/users.get', params = {'access_token': token, 'user_ids': user_id, 'fields': 'city', 'name_case': i,  'v': 5.103}).json()
	write_json(r)
	global a
	a = r['response'][0]['city']['title']

def get_html(url):
	r = requests.get(url)
	return r.text

def get_total_pages(html):
	soup = BeautifulSoup(html, 'lxml')
	pages = soup.find('div', class_='pager')
	if (pages is None):
		return 0
	pager = pages.find_all('a', class_='b-pager2__page')[-1].get('href')
	if (pager is None):
		return 1
	total_pages = pager.split('=')[-1]

	return int(total_pages)

def get_total_categories(html):
	soup = BeautifulSoup(html, 'lxml')
	categories = soup.find_all('div', class_='b-search-categories__short-item')
	if (categories is None):
		return 0
	for i in range(0, len(categories) - 2):
		categories[i] = categories[i].find_all('a', class_='')
		categories[i] = categories[i][-1].get('href')

	return categories

def get_categories_name(html):
	soup = BeautifulSoup(html, 'lxml')
	categories = soup.find_all('div', class_='b-search-categories__short-item')
	categories_name = []
	if (categories is None):
		return 0
	for i in range(0, len(categories) - 2):
		categories[i] = categories[i].find_all('a', class_='')
		s = categories[i][0].find_all(text=True, recursive=False)
		categories_name.append(s[0])
	return categories_name

def parse(request):
	global d
	d[request] = {}
	url = '*some url*' + request
	categories_name = get_categories_name(get_html(url))
	categories = get_total_categories(get_html(url))
	total_categories = len(categories)
	url_part = '&page='

	if (total_categories == 0):
		print("Сорри, товаров нет")

	for i in range(0, min(total_categories - 2, 5)):
		inter_url = '*some url*' + categories[i]
		inter_pages = get_total_pages(get_html(inter_url))
		min_price = 10000000000000
		name = ''
		product_link = ''
		for j in range(0, min(5, inter_pages)):
			total_url = inter_url + url_part + str(j)
			soup = BeautifulSoup(get_html(total_url), 'lxml')
			products = soup.find_all('div', class_='b-item-tile__wrapper')
			for k in range(0, len(products)):
				link = products[k].find('a', class_='b-price-link')
				if not(link is None):
					price = link.find_all(text=True, recursive=False)
					price = price[0].replace('p.', '')
					price = price.replace(' ', '')
					if (int(price) < min_price):
						name = link['aria-label']
						min_price = int(price)
						product_link = link['data-hidelink']
		if (name != ''):
			d[request][categories_name[i]] = (name, '*some url*' + product_link, min_price)

# Авторизуемся как сообщество 
vk = vk_api.VkApi(token=token) 

# Работа с сообщениями 
longpoll = VkLongPoll(vk)

m = {}

# Основной цикл 
for event in longpoll.listen():

	# Если пришло новое сообщение 
	if event.type == VkEventType.MESSAGE_NEW: 

		# Если оно имеет метку для меня( то есть бота) 
		if event.to_me: 

			# Сообщение от пользователя 
			request = event.text 
			user_id = event.user_id
			try:
				m[user_id]["want"] = m[user_id]["want"]
			except:
				m[user_id] = {}
				m[user_id]["want"] = 0
				m[user_id]["prev_request"] = ''
				m[user_id]["seller"] = 0
				m[user_id]["name"] = ''
				m[user_id]["category_name"] = ''
				m[user_id]["link"] = ''
				m[user_id]["price"] = 0
			# Каменная логика ответа
			if (request == "Назад"):
				write_msg_before(user_id, "Что-нибудь ещё?")
				m[user_id]["want"] = 0
				m[user_id]["seller"] = 0
			elif (request == "Хочу приобрести товар" and m[user_id]["want"] == 0 and m[user_id]["seller"] == 0):
				write_msg_after(user_id, "Какой товар хочешь приобрести?")
				m[user_id]["want"] = 1
			elif (request == "Хочу продать товар" and m[user_id]["want"] == 0 and m[user_id]["seller"] == 0):
				write_msg_after(user_id, "Какой товар хочешь продать?")
				m[user_id]["seller"] += 1
			elif (m[user_id]["seller"] == 1):
				m[user_id]["name"] = request
				d[request] = {}
				write_msg_after(user_id, "К какой категории будет принадлежать твой товар?")
				m[user_id]["seller"] += 1
			elif (m[user_id]["seller"] == 2):
				m[user_id]["category_name"] = request
				write_msg_after(user_id, "По какой цене ты хочешь его продать?")
				m[user_id]["seller"] += 1
			elif (m[user_id]["seller"] == 3):
				m[user_id]["price"] = int(request)
				write_msg_after(user_id, "Дай ссылку на товар")
				m[user_id]["seller"] += 1
			elif (m[user_id]["seller"] == 4):
				m[user_id]["link"] = request
				d[m[user_id]["name"]][m[user_id]["category_name"]] = (m[user_id]["name"], m[user_id]["link"], m[user_id]["price"])
				write_msg_before(user_id, "Отлично, ваш товар добавлен!")
				m[user_id]["seller"] = 0
			elif (m[user_id]["want"] == 1):
				if not(request in d):
					parse(request)
				global categories_name
				ans = 'Выбери категорию из списка ниже:\n'
				for key in d[request]:
					ans += key
					ans += "\n"
				write_msg_after(user_id, ans)
				m[user_id]["prev_request"] = request
				m[user_id]["want"] = 2
			elif (m[user_id]["want"] == 2):
				try:
					write_msg_after(user_id, d[m[user_id]["prev_request"]][request][0] + '\n' + 'Цена: ' + str(d[m[user_id]["prev_request"]][request][2]) + ' р.' + '\n' + d[m[user_id]["prev_request"]][request][1])
				except:
					write_msg_after(user_id, 'Не нашёл товаров')
				m[user_id]["want"] = 1
			else:
				write_msg_before(user_id, "Привет! Я RBBot. Помогу тебе приобрести любой товар в твоём городе по выгодной цене. Хочешь что-то приобрести?")
				m[user_id]["want"] = 0
				m[user_id]["seller"] = 0

			random_id=random_id+1
			i = 0
			s = 0
			while i < len(ID):
				if ID[i] > 0 and user_id != ID[i]:
					s += 1
				i += 1
			if s == len(ID):
				ID.append(user_id)				
				info()
			print(s)
