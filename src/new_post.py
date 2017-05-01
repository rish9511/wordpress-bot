import re
from bs4 import BeautifulSoup
import requests


def get_form_data(session, url, title):

	try:
		url = url + "wp-admin/post-new.php"
		r = session.get(url)

	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return None

	if r.status_code == requests.codes.ok:
		soup = BeautifulSoup(r.content, "lxml")
		_wpnonce = soup.find("input", id="_wpnonce")["value"]
		user_ID = soup.find("input", id="user-id")["value"]
		action = soup.find("input", id="hiddenaction")["value"]
		originalaction = soup.find("input", id="originalaction")["value"]
		post_author = soup.find("input", id="post_author")["value"]
		original_post_status = soup.find("input", id="original_post_status")["value"]
		referredby = soup.find("input", id="referredby")["value"]
		auto_draft = soup.find("input", id="auto_draft")["value"]
		post_ID = soup.find("input", id="post_ID")["value"]
		meta_box_order_nonce = soup.find("input", id="meta-box-order-nonce")["value"]
		closedpostboxesnonce = soup.find("input", id="closedpostboxesnonce")["value"]
		return {
			"_wpnonce": _wpnonce,
			"user_ID": user_ID,
			"action": action,
			"originalaction": originalaction,
			"post_author": post_author,
			"original_post_status": original_post_status,
			"referredby": referredby,
			"auto_draft": auto_draft,
			"post_ID": post_ID,
			"meta-box-order-nonce": meta_box_order_nonce,
			"closedpostboxesnonce": closedpostboxesnonce,
			"post_title": title
		}

	return None


def find_title():
	try:
		with open("../article.txt", "r") as file_obj:
			for line in file_obj:
				if line.strip().startswith("00"):
					return line.replace("00", "", 1)

	except IOError as e:
		return None

	return None


def create_post(session, url, form_data):
	try:
		url = url + "wp-admin/post.php"
		r = session.post(url, data=form_data)

	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return False

	if r.status_code == requests.codes.ok:
		return True

	return False


def create_new_post(session, url):

	'''
		step 1: find the title of the article
		step 2: get the form data wich we will be used while creating the new post
		step 3: create the post
	'''
	title = find_title()

	if not title:
		title = "title_not_found"

	form_data = get_form_data(session, url, title)
	if form_data:
		if create_post(session, url, form_data):
			try:
				with open("../id.txt", "w") as file_obj:
					file_obj.write(form_data["post_ID"])
			except IOError as e:
				# does not make much sense. The post has been created successfully but we could not store the post id
				# since there was an error in opening the file.
				# What could be a better solution ?
				return False
			return True

	return False
