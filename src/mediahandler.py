import re
from bs4 import BeautifulSoup
import requests
import wget
import os
from amazon.api import AmazonAPI
import json

special_characters = [" ", ",", "'", '"', "(", ")", "/", "&", "\xc2", "\xa0", "\xae", "$", ";"]


def login():
	data = {'log': "pool_admin", 'pwd': 'g10Sq2I69TDjBmd'}
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'}

	try:
		session = requests.Session()
		r = session.post("http://shikhargupta.in/pool/wp-login.php", data=data, headers=headers)
	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return None

	if r.status_code == 200:
		return session

	return None


def get_form_data(session, title):

	try:
		url = "http://shikhargupta.in/pool/wp-admin/media-new.php"
		r = session.get(url)

	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return None
	if r.status_code == 200:
		_wpnonce = ""
		short = ""
		post_id = ""
		soup = BeautifulSoup(r.content, "lxml")
		scripts = soup.find_all("script", {"type": "text/javascript"})
		for elem in scripts:
			if "wpUploaderInit" in elem.text:
				_wpnonce = re.search('_wpnonce\":"(\w+)"', elem.text).group(1)
				short = re.search('short\":"(\w+)"', elem.text).group(1)
				post_id = re.search('post_id\":(\w+),', elem.text).group(1)
				break
		data = {
			"name": title,
			"action": "upload-attachment",
			"_wpnonce": _wpnonce
		}
	return data


def get_image_url(response):
	response = re.search("{.*", response)
	response = json.loads(response.group(0))
	return response["data"]["url"]


def upload_image(session, title):

	for sc in special_characters:
			if sc in title:
				title = title.replace(sc, "_")
	title = title + ".jpg"
	form_data = get_form_data(session, title)
	if form_data:

		with open("../%s" % (title), "r") as img:
			files = {"async-upload": img}
			try:
				url = "http://shikhargupta.in/pool/wp-admin/async-upload.php"
				r = session.post(url, data=form_data, files=files)

			except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
				return None
			# remove hex characters from content and the load json from it. get the url and return it

		return get_image_url(r.content)


def move_and_resize(filename, title):
	# change the name of the file
	for sc in special_characters:
		if sc in title:
			title = title.replace(sc, "_")
	title = title + ".jpg"
	title = "../" + title
	move = 'mv %s %s' % (filename, title)
	resize = 'convert %s -resize 300x300 %s' % (title, title)
	try:
		os.system(move)
		os.system(resize)
	except OSError as e:
		print e
		return False

	return True


def download_image(ansi):
	try:
		amazon = AmazonAPI("AKIAI6QK73F3SFYOOI2A", "DeOYip7bDtrTMb1qnMtW+ZkaMmJPEJ2c4ZVrBsRc", "1003d1-20")
		product = amazon.lookup(ItemId=ansi)
		filename = wget.download(product.large_image_url)
	except Exception as e:
		print e
		return False
	return {'file': filename, 'title': product.title}


def find_ansi():
	ansi_dict = {}
	try:
		with open("../article.txt", "r") as file_obj:
			for line in file_obj:
				if line.strip().startswith("07"):
					amazon_link = line.replace("07", "", 1)
					ansi = re.search("dp/(\w*)/?", amazon_link)
					if ansi:
						ansi_dict[amazon_link] = ansi.group(1)
	except IOError as e:
		print e
		return None 

	return ansi_dict


def download_and_upload_images(session):
	img_details = {}
	ansi_dict = find_ansi()
	for amazon_link in ansi_dict:
		details = download_image(ansi_dict[amazon_link])
		if details:
			if move_and_resize(details["file"], details["title"]):
				source_url = upload_image(session, details["title"])
				if source_url:
					img_details[amazon_link] = source_url

	with open("../article_details.txt", "w") as json_file:
		json.dump(img_details, json_file)


session = login()
download_and_upload_images(session)