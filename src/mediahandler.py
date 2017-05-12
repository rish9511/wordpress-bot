import re
from bs4 import BeautifulSoup
import requests
import wget
import os
from amazon.api import AmazonAPI
import json
import time


def get_form_data(session, title, site_url):

	try:
		url = site_url + "wp-admin/media-new.php"
		r = session.get(url)

	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return None

	if r.status_code == requests.codes.ok:

		_wpnonce = ""
		soup = BeautifulSoup(r.content, "lxml")
		scripts = soup.find_all("script", {"type": "text/javascript"})

		for elem in scripts:
			if "wpUploaderInit" in elem.text:

				if re.search('_wpnonce\":"(\w+)"', elem.text):
					_wpnonce = re.search('_wpnonce\":"(\w+)"', elem.text).group(1)
					break
		data = {
			"name": title,
			"action": "upload-attachment",
			"_wpnonce": _wpnonce
		}
	return data


def get_image_url(response):

	try:

		if re.search("{.*", response):
			response = json.loads(re.search("{.*", response).group(0))
			return response["data"]["url"]

	except (ValueError, AttributeError) as e:
		return None

	return None


def upload_image(session, title, site_url):

	title = title + ".jpg"

	form_data = get_form_data(session, title, site_url)

	if form_data:

		try:

			with open("../%s" % (title), "r") as img:
				files = {"async-upload": img}
				site_url = site_url + "wp-admin/async-upload.php"
				r = session.post(site_url, data=form_data, files=files)

		except (IOError, requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
			return None
			# remove hex characters from content and the load json from it. get the url and return it

		return get_image_url(r.content)

	return None


def move_and_resize(filename, title):
	# change the name of the file

	try:
		title = title + ".jpg"
		title = "../" + title
		move = 'mv %s %s' % (filename, title)
		resize = 'convert %s -resize 300x300 %s' % (title, title)

		os.system(move)
		os.system(resize)
	except OSError as e:
		return False

	return True


def rename_title(title, index):
	try:

		unicode_expr = "([^\u0000-\u007F]+)"
		hexchar_expr = "([^\x00-\x7F]+)"
		non_alphanumeric_expr = "([^\w]+)"

		unicode_chars = re.findall(unicode_expr, title)
		for chars in unicode_chars:
			title = title.replace(chars, "_")

		hex_chars = re.findall(hexchar_expr, title)
		for chars in hex_chars:
			title = title.replace(hex_chars, "_")

		non_alphanumeric_chars = re.findall(non_alphanumeric_expr, title)
		for chars in non_alphanumeric_chars:
			title = title.replace(chars, "_")

		return title
	except Exception as e:
		return "Unnamed_%s" % (index)


def download_image(ansi, index):
	try:
		amazon = AmazonAPI("AKIAI6QK73F3SFYOOI2A", "DeOYip7bDtrTMb1qnMtW+ZkaMmJPEJ2c4ZVrBsRc", "1003d1-20")
		product = amazon.lookup(ItemId=ansi)
		filename = wget.download(product.large_image_url)
	except Exception as e:
		# product not available through amazon's product api.
		return False
	title = rename_title(product.title, index)
	return {'file': filename, 'title': title}


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
		return None

	return ansi_dict


def download_and_upload_images(session, site_url):
	'''
		* step 1: read the article and the find the ansi of all the products
		* step 2: using the ansi download the images
		* step 3: move and resize the images to different folder
		* step 4: upload the images
		* returns true always - This is because we can post the artilces without images.
	'''
	img_details = {}
	ansi_dict = find_ansi()
	for (index, amazon_link) in enumerate(ansi_dict):
		details = download_image(ansi_dict[amazon_link], index)
		if details:
			if move_and_resize(details["file"], details["title"]):
				image_url = upload_image(session, details["title"], site_url)
				if image_url:
					img_details[amazon_link] = image_url

		time.sleep(3)

	with open("../article_details.txt", "w") as file_obj:
		json.dump(img_details, file_obj)

	return True
