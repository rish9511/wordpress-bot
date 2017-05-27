import re
from bs4 import BeautifulSoup
import requests
import wget
import os
from amazon.api import AmazonAPI
import json
import time
from HTMLParser import HTMLParseError


def get_form_data(session, title, site_url):

	try:
		url = site_url + u"wp-admin/media-new.php"
		r = session.get(url)

	except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.exceptions.RequestException) as e:
		return None

	if r.status_code == requests.codes.ok:
		try:
			_wpnonce = ""
			soup = BeautifulSoup(r.content, "lxml")
			scripts = soup.find_all("script", {"type": "text/javascript"})

			for elem in scripts:
				if "wpUploaderInit" in elem.text:

					if re.search('_wpnonce\":"(\w+)"', elem.text):
						_wpnonce = re.search('_wpnonce\":"(\w+)"', elem.text).group(1)
						break
			if _wpnonce:
				data = {
					"name": title,
					"action": "upload-attachment",
					"_wpnonce": _wpnonce
				}
				return data

		except (re.error, HTMLParseError, IndexError, AttributeError) as e:
			return None

	return None


def get_image_url(response):

	try:
		response = response.decode('utf-8', errors='ignore')
	except (UnicodeError) as e:
		pass

	try:

		if re.search(u"{.*", response):
			response = json.loads(re.search(u"{.*", response).group(0))
			return response["data"]["url"]

	except (LookupError, AttributeError, re.error,) as e:
		return None

	return None


def upload_image(session, title, site_url):

	title = title + u".jpg"

	form_data = get_form_data(session, title, site_url)

	if form_data:

		try:

			with open("../%s" % (title), "r") as img:
				files = {"async-upload": img}
				site_url = site_url + u"wp-admin/async-upload.php"
				r = session.post(site_url, data=form_data, files=files)

		except (IOError, requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.exceptions.RequestException) as e:
			return None

		# remove hex characters from content and the load json from it. get the url and return it
		return get_image_url(r.content)

	return None


def move_and_resize(filename, title):
	# change the name of the file

	try:
		title = title + u".jpg"
		title = u"../" + title
		move = 'mv %s %s' % (filename, title)
		resize = 'convert %s -resize 300x300 %s' % (filename, filename)

		os.system(resize)
		os.system(move)
	except (OSError, UnboundLocalError) as e:
		# UnboundLocalError: Raised when a reference is made to a local variable in a function or method, but no value has been bound to that variable
		# Reason: file was not named properly
		return False

	return True


def rename_title(title, index):

	try:

		if isinstance(title, unicode):
			title = title.encode('utf-8', errors='ignore')

		title = title.decode('utf-8', errors='ignore')

	except (UnicodeDecodeError, UnicodeEncodeError) as e:
		pass

	try:

		title = title.replace(' ', '')

		unicode_expr = u"([^\u0000-\u007F]+)"
		hexchar_expr = u"([^\x00-\x7F]+)"
		non_alphanumeric_expr = u"([^\w]+)"

		unicode_char = re.search(unicode_expr, title)
		while(unicode_char):
			title = title.replace(unicode_char.group(), "_")
			unicode_char = re.search(unicode_expr, title)

		hex_char = re.search(hexchar_expr, title)
		while(hex_char):
			title = title.replace(hex_char.group(), "_")
			hex_char = re.search(hexchar_expr, title)

		non_alphanumeric_char = re.search(non_alphanumeric_expr, title)
		while(non_alphanumeric_char):
			title = title.replace(non_alphanumeric_char.group(), "_")
			non_alphanumeric_char = re.search(non_alphanumeric_expr, title)

		# just a precaution. All the '"' should have been removed by the non_alphanumeric_expr
		title = title.replace('"', "_")

		return title
	except (re.error, UnicodeError) as e:
		return u"Unnamed_%s" % (index)


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
				try:
					line = line.decode('utf-8', errors='ignore')
				except (UnicodeDecodeError, UnicodeEncodeError) as e:
					# could not convert the line to unicode type.
					pass
				if line.strip().startswith("07"):
					amazon_link = line.replace("07", "", 1)
					ansi = re.search(u"dp/(\w*)/?", amazon_link)
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
	images_with_issues = []

	ansi_dict = find_ansi()

	for (index, amazon_link) in enumerate(ansi_dict):

		details = download_image(ansi_dict[amazon_link], index)

		if details:
			if u"Unnamed_" in details["title"]:
				images_with_issues.append(amazon_link)

			if move_and_resize(details["file"], details["title"]):
				image_url = upload_image(session, details["title"], site_url)
				if image_url:
					img_details[amazon_link] = image_url
				else:
					# upload failed
					images_with_issues.append(amazon_link)
			else:
				# move and resize failed
				images_with_issues.append(amazon_link)
		else:
			# download failed
			images_with_issues.append(amazon_link)

		time.sleep(6)

	with open("../article_details.txt", "w") as file_obj:
		json.dump(img_details, file_obj)

	with open("../images_not_uploaded.txt", "w") as file_obj:
		for images_link in images_with_issues:
			file_obj.write(images_link)
			file_obj.write("\n")

	return True
