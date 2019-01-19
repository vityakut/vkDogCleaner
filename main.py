#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
:authors: vityakut
:license: MIT License
:url: https://github.com/vityakut/vkDogCleaner
:copyright: (c) 2019 vityakut
"""
import vk_api
import time
import qtoml
import os
import re

global config
global session
global tmp_path


def captcha_handler(captcha):
	url = captcha.get_url()
	key = input("Enter captcha code {0}: ".format(url)).strip()
	return captcha.try_again(key)


def log_to_file(arrlog, file="log"):
	if not os.path.isdir(tmp_path):
		os.makedirs(tmp_path)
	file = open(os.path.join(tmp_path, file), 'a')
	for line in arrlog:
		file.write("%s\n" % line)
	file.close()


def vk_login():
	global session
	session = vk_api.VkApi(
		login=config['login'],
		password=config['password'],
		app_id=config['app']['id'],
		captcha_handler=captcha_handler,
		api_version="5.92",
	)
	try:
		session.auth()
		user = session.get_api().users.get()
		print("Login complete as {0} {1} (https://vk.com/id{2})".format(
			user[0]['first_name'], user[0]['last_name'], user[0]['id']))
		return session
	except vk_api.AuthError as error_msg:
		print(error_msg)
		return
	except vk_api.VkApiError as error_msg:
		print(error_msg)
		return


def get_config(conf_file='config.toml'):
	global config
	curr_path = os.path.dirname(os.path.realpath(__file__))
	if os.path.isfile(os.path.join(curr_path, conf_file)):
		infile = open(conf_file, 'r')
		config = qtoml.load(infile)
		return config
	else:
		exit(str(os.path.join(curr_path, conf_file)) + " not found")


def get_groups_ids(groups):
	resgr = []
	for group in groups:
		res = (re.sub(r'^(https{0,1}://){0,1}vk.com/', '', group))
		res = (re.sub(r'^club', '', res))
		res = (re.sub(r'^public', '', res))
		resgr.append(res)
	api = session.get_api()
	result = api.groups.getById(group_ids=",".join(resgr))
	resgr = [i['id'] for i in result]
	return resgr


def get_blocked_users_from_tmp(gid):
	file_tmp = os.path.join(tmp_path, "%s.tmp" % str(gid))
	if os.path.isfile(file_tmp):
		file = open(file_tmp, 'r')
		arr = [row.strip() for row in file]
		file.close()
		return arr
	else:
		print(str(file_tmp) + " not found")
		return False


def get_blocked_users(gid):
	file_tmp = os.path.join(tmp_path, "%s.tmp" % str(gid))
	page = 0
	limit = 1000
	banned = []
	if os.path.isfile(file_tmp):
		os.remove(file_tmp)

	api = session.get_api()
	tmp = api.groups.getById(group_id=gid)
	print("Получение подписчиков из {1} (https://vk.com/{0})".format(tmp[0]['screen_name'], tmp[0]['name']))

	while True:
		offset = page * limit
		res = api.groups.getMembers(group_id=gid, offset=offset, count=limit, fields='city, sex, bdate')
		total = res['count']
		# total = 15
		for item in res['items']:
			if 'deactivated' in item.keys():
				banned.append(item['id'])
		page = page + 1
		if total < offset + limit:
			break
		else:
			time.sleep(1/3)

	print("{0} собак из {1} пользователей".format(len(banned), total))
	log_to_file(banned, file_tmp)
	return banned


def remove_blocked_users(gid, blocked):
	total_blocked = len(blocked)
	clear_mode = config['clear_mode']
	clear_percent = config['clear_percent']
	clear_count = config['clear_count']
	api = session.get_api()
	if clear_mode == 0:
		clear_count = total_blocked
	elif clear_mode == 1:
		clear_count = round((total_blocked / 100) * clear_percent)
	elif clear_mode == 3:
		perc_count = round((total_blocked / 100) * clear_percent)
		if perc_count < clear_count:
			clear_count = perc_count
		if clear_count > total_blocked:
			clear_count = total_blocked
	else:
		clear_count = config['clear_count']
		if clear_count > total_blocked:
			clear_count = total_blocked
	print("Будет удалено {0} собак".format(clear_count))
	i = 0
	while i < clear_count:
		try:
			res = api.groups.removeUser(group_id=int(gid), user_id=blocked[i])
			if res:
				print("{0} id{1} удален из {2}".format(i, blocked[i], gid))
			i += 1
		except vk_api.VkApiError as error_msg:
			print(error_msg)
			return False


def main():
	print("Start")
	if not get_config():
		exit("Error! Config not found")
	outfile = open('new_filename.toml', 'w')
	qtoml.dump(config, outfile)
	vk_login()
	print("--------------")
	groups = get_groups_ids(config['groups'])
	for gid in groups:
		blocked = get_blocked_users(gid)
		# blocked = get_blocked_users_from_tmp(gid)
		if blocked:
			remove_blocked_users(gid, blocked)
		print("--------------")


if __name__ == '__main__':
	tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")
	input("start")
	main()
