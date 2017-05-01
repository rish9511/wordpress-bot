import requests
from bs4 import BeautifulSoup
import re
import json
from requests_oauthlib import OAuth1
from json import dumps


def push_back(text, code, amazon_link="", source_url=""):
	if code == 01:
		text = '<p>' + text + '</p>'
		return text
	if code == 10:
		anchor_tag = '''\
		<a href=%s target="_blank" rel="nofollow" class="">''' % (amazon_link)
		text = ' <h3 class="">' + anchor_tag + text + '</a>' + '</h3>'
		return text
	if code == 11:
		text = '<h4 class="">' + text + '</h4>'
		return text
	if code == 100:
		list_tag = '''\
		<ul>
		<li class="tve_empty_dropzone">
		<p>
		'''
		closing_tag = '</p></li></ul>'
		text = list_tag + text + closing_tag
		return text
	if code == 101:
		price_tag = '''
		<div class="thrv_wrapper thrv_button_shortcode tve_centerBtn" data-tve-style="1">
		<div class="tve_btn tve_nb tve_normalBtn tve_btn1 tve_blue">
		<a href=%s class="tve_btnLink" target="_blank" rel="nofollow" style="font-size: 16px; line-height: 16px;">
		<span class="tve_left tve_btn_im">
		<i></i>
		<span class="tve_btn_divider"></span>
		</span>
		<span class="tve_btn_txt">CHECK THE LATEST PRICE ON AMAZON</span>
		</a>
		</div>
		</div>
		<br><br>''' % (text)
		text = price_tag
		return text
	if code == 110:
		image_tag = '''\
		<div style="" class="thrv_wrapper tve_image_caption alignleft">
		<span class="tve_image_frame">
		<a href=%s target="_blank" rel="nofollow" class="">
		<img class="tve_image" alt="" style="" src=%s>
		</a>
		</span>
		</div>''' % (amazon_link, source_url)
		text = image_tag + text
		return text
	if code == 1000:
		text = ' <h3 class="">' + text + '</h3>'
		return text


def prepare_article_html():

	details = {}

	# does not matter whether we have article_details file or not.
	# If we have have it and it's not empty, we will have images in the article otherwise not
	try:
		with open("../article_details.txt", "r") as json_file:
			details = json.load(json_file)
	except IOError as e:
		pass

	try:
		with open("../article.txt", "r") as file_obj:

			article_html = ""
			amazon_link = ""
			for line in file_obj:
				if line.strip().startswith("00"):
					continue
				if line.strip().startswith("01"):
					txt = line.replace("01", "").decode('utf-8')

					article_html += push_back(txt, 01)

				if line.strip().startswith("02"):
					txt = line.replace("02", "").decode('utf-8')
					article_html += push_back(txt, 10, amazon_link)

				if line.strip().startswith("03"):
					txt = line.replace("03", "").decode('utf-8')
					article_html += push_back(txt, 11)

				if line.strip().startswith("04"):
					txt = line.replace("04", "").decode('utf-8')
					article_html += push_back(txt, 100)

				if line.strip().startswith("05"):
					txt = line.replace("05", "").decode('utf-8')
					article_html += push_back(txt, 101)

				if line.strip().startswith("06"):
					txt = line.replace("06", "").decode('utf-8')
					source_url = ""
					try:
						source_url = details[amazon_link]
					except KeyError as e:
						continue
					article_html += push_back(txt, 110, amazon_link, source_url)

				if line.strip().startswith("07"):
					txt = line.replace("07", "", 1)
					amazon_link = txt

				if line.strip().startswith("08"):
					txt = line.replace("08", "").decode('utf-8')
					article_html += push_back(txt, 1000)

			return article_html

	except IOError as e:
		return None


def get_thrive_plugin_page(session, website_url):

	try:
		with open("../id.txt", "r") as file_obj:
			post_id = file_obj.read()
			if post_id:

				website_url = website_url + "?p=%s&tve=true" % (post_id)
				resp = session.get(website_url)

				if resp.status_code == requests.codes.ok:
					return resp

	except (IOError, requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return None

	return None


def find_nonce(session, website_url):

	'''
		Since the we use thrive content builder plugin to post the articles, we have to find the nonce on the plugin's
		page
		* Step 1: Using the id of the post, get the plugin page
		* Step 2: Scrape the page and find the nonce
	'''
	response = get_thrive_plugin_page(session, website_url)

	if response:
		soup = BeautifulSoup(response.text, 'lxml')
		scripts = soup.find_all("script", {"type": "text/javascript"})
		for tag in scripts:
			if tag.text:
				nonce = re.search('"nonce":"(.*)",', tag.text)

				nonce_2 = re.search('"nonce":{"sendToEditor":"(\w*)"},', tag.text)

				if nonce:
					return nonce.group(1)
				if nonce_2:
					return nonce_2.group(1)
	return None


def post(session, nonce, html_article, website_url):

	try:
		with open("../id.txt", "r") as file_obj:
			post_id = file_obj.read()
			if post_id:
				form_data = {
					"action": "tve_save_post",
					"tve_content": html_article,
					"post_id": post_id,
					"security": str(nonce),
					"update": "true",
					"inline_rules": "",
					"tve_custom_css": "",
					"tve_landing_page": "",
					"tve_globals[e]": 1,
					"tve_global_scripts[head]": "",
					"tve_global_scripts[footer]": "",
					"has_icons": 0,
					"tve_default_tooltip_settings": ""
				}
				website_url = website_url + "wp-admin/admin-ajax.php"
				headers = {
					'content-type': "application/x-www-form-urlencoded"
				}
				resp = session.post(website_url, data=form_data, headers=headers)
				if resp.status_code == requests.codes.ok:
					return True

	except (IOError, requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		return False

	return False


def post_article(session, website_url):
	'''
		* step 1: find the nonce. Needs to be sent in form_data
		* step 2: prepare the article in html format
		* step 3: post the article
	'''
	nonce = find_nonce(session, website_url)

	if nonce:
		html_article = prepare_article_html()
		if html_article:
			if post(session, nonce, html_article, website_url):
				return True
	return False
