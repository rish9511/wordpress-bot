import re
from bs4 import BeautifulSoup
import requests


def get_form_data(session):

	try:
		url = "http://shikhargupta.in/pool/wp-admin/post-new.php"
		r = session.get(url)

	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return None

	if r.status_code == 200:
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
		post_title = "python_post"
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
			"post_title": "python_post"
		}

	return None


def create_new_post(session):
	form_data = get_form_data(session)
	if form_data:
		try:
			url = "http://shikhargupta.in/pool/wp-admin/post.php"
			r = session.post(url, data=form_data)

		except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
			return False
		if r.status_code == 200:
			return True
		return False
	return False
