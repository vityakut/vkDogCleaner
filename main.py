import vk_api
import time
import qtoml
import os

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
		captcha_handler=captcha_handler)
	try:
		session.auth()
		print("Login complete")
		return session
	except vk_api.AuthError as error_msg:
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
	print("get users from {0}".format(gid))
	file_tmp = os.path.join(tmp_path, "%s.tmp" % str(gid))
	total = 0
	page = 0
	offset = 0
	limit = 1000
	banned = []
	if os.path.isfile(file_tmp):
		os.remove(file_tmp)

	api = session.get_api()
	tmp = api.groups.getById(group_id=gid)
	print("https://vk.com/{0} - {1}".format(tmp[0]['screen_name'], tmp[0]['name']))

	while True:
		offset = page * limit
		res = api.groups.getMembers(group_id=gid, offset=offset, count=limit, fields='city, sex, bdate', version='5.92')
		total = res['count']
		# total = 15
		for item in res['items']:
			if ('deactivated' in item.keys()):
				banned.append(item['id'])
		page = page + 1
		if total < offset + limit:
			print('DONE')
			break
		else:
			print(str(page) + ' SLEEP')
			time.sleep(1/3)
	print(len(banned))
	log_to_file(banned, file_tmp)
	return banned


def remove_blocked_users(gid, blocked):
	total_blocked = len(blocked)
	clear_mode = config['clear_mode']
	clear_percent = config['clear_percent']
	clear_count = config['clear_count']
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


def main():
	print("Start")
	get_config()
	print(config)
	vk_login()
	print("--------------")
	for gid in config['groups']:
		# blocked = get_blocked_users(gid)
		blocked = get_blocked_users_from_tmp(gid)
		if blocked:
			remove_blocked_users(gid, blocked)


if __name__ == '__main__':
	tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")
	main()
