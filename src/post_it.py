import requests
from bs4 import BeautifulSoup
import re
import json
from requests_oauthlib import OAuth1
from json import dumps

session_obj = None


def login():
	global session_obj
	data = {'log': "admin_guitar", 'pwd': 'Hello@123'}
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'}
	try:
		session = requests.Session()
		r = session.post("https://guitarlair.com/wp-login.php", data=data, headers=headers)
	except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
		print e
		return None
	print r
	print r.status_code
	session_obj = session
	return session


def init():
	session = login()
	with open("../id.txt", "r") as file_obj:
		post_id = file_obj.read()
	if post_id:
		if session:
			try:
				url = "https://guitarlair.com/?p=%s&tve=true" % (post_id)
				resp = session.get(url)
			except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
				print e
				return None
			return resp
		return None
	return None


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
	with open("../article_details.txt", "r") as json_file:
		details = json.load(json_file)

	try:
		file_obj = open("../article.txt", "r")
	except IOError as e:
		return None
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
				print e
			article_html += push_back(txt, 110, amazon_link, source_url)

		if line.strip().startswith("07"):
			txt = line.replace("07", "", 1)
			amazon_link = txt

		if line.strip().startswith("08"):
			txt = line.replace("08", "").decode('utf-8')
			article_html += push_back(txt, 1000)

	file_obj.close()
	return article_html


def find_nonce(response):
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


def post_article(nonce, article_html):
	post_id = ""
	with open("../id.txt", "r") as file_obj:
		post_id = file_obj.read()
	if post_id:
		form_data = {
			"action": "tve_save_post",
			"tve_content": article_html,
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
		url = "https://guitarlair.com/wp-admin/admin-ajax.php"
		headers = {
			'content-type': "application/x-www-form-urlencoded"
		}
		try:
			resp = session_obj.post(url, data=form_data, headers=headers)
		except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
			print e
			return None
		return resp
	else:
		print "no post id found"
		return None


def post_with_rest(article_html):
	if article_html:
		try:
			with open("../id.txt", "r") as file_obj:
				post_id = file_obj.read()
			auth = OAuth1('I5fmc39EQxmD', 'efErrizGbZ92FmMk4ui2PoBv0oVrYvrR1OgzdUzWsxE96A79', 'BYs5GZiocJxwA3TEAMXaA12p', 'agkUOI03IfEbqoSmiVw0v49nIufIfreA0Q3X5i9yCNABfxgy')
			data = {'content': article_html}
			url = "https://guitarlair.com/wp-json/wp/v2/posts/%s" % (post_id)
			resp = requests.post(url, auth=auth, data=data)
		except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
			print e
			return False

		print resp.status_code
		return True

	return False

response = init()
if response:
	# prepare_article_html
	article_html = prepare_article_html()
	nonce = find_nonce(response)
	if article_html and nonce:
		# post the article
		resp = post_article(nonce, article_html)
		if resp:
			print resp.status_code
		else:
			print "could not post. trying to post using rest api ..."
	else:
		# try with rest api
		print "fuck it"
		# posted = post_with_rest(article_html)
		# if posted:
		# 	print "posted with rest api"
		# else:
		# 	print "could not post with rest api"
