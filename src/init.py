# -*- coding: UTF-8 -*-
from download_article import article_download
from edit_article import start_editing
from mediahandler import download_and_upload_images
from new_post import create_new_post
from post_it import post_article
from remove_everything import remove_files
from mailer import mail_the_report

import requests
import json

images_not_uploaded = ""


def login(website, user_name, password):

	if website and user_name and password:
		data = {'log': user_name, 'pwd': password}
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'}
		try:
			session = requests.Session()
			website = website + u"wp-login.php"
			r = session.post(website, data=data, headers=headers)
		except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.exceptions.RequestException) as e:
			return False

		if r.status_code == requests.codes.ok:
			return session

	return False


def prepare_artilce_report(website, article_link, posted):

	global images_not_uploaded
	article_report = ""
	try:
		with open("../images_not_uploaded.txt", "r") as file_obj:
			link = file_obj.readline()
			if link:
				article_report += "product_link: " + link
				article_report += "\n\n"

		if article_report:
				artilce_report = "article_link: " + article_link + "\n\n" + article_report + "------------------------------------------------------------\n\n"
				images_not_uploaded += artilce_report
	except IOError:
		return


def start_processing(form_data, session):

	global images_not_uploaded
	articles = form_data["articles"]
	website = form_data["website"]
	articles_received = 0
	articles_posted = 0
	articles_not_posted = ''
	for article_link in articles:

		if article_link:
			articles_received += 1
			downloaded = article_download(article_link)
			if downloaded:
				edit_done = start_editing(form_data["tag"])
				if edit_done:
					post_created = create_new_post(session, form_data["website"])
					if post_created:

						if download_and_upload_images(session, form_data["website"]):  # the function always returns true, hence we don't have an else block
							if post_article(session, form_data["website"]):
								articles_posted += 1
								prepare_artilce_report(website, article_link, True)

							else:
								prepare_artilce_report(website, article_link, False)
								articles_not_posted += "\n" + "link: " + article_link + "\n"

					else:
						prepare_artilce_report(website, article_link, False)
						articles_not_posted += "\n" + "link: " + article_link + "\n"
				else:
					prepare_artilce_report(website, article_link, False)
					articles_not_posted += "\n" + "link: " + article_link + "\n"

			else:
				prepare_artilce_report(website, article_link, False)
				articles_not_posted += "\n" + "link: " + article_link + "\n"

			# remove all the files irrespective of whether the article got posted or not
			remove_files()

	if images_not_uploaded:
		images_not_uploaded = "\nWebsite: " + website + "\n\n" + images_not_uploaded
	mail_the_report(images_not_uploaded, articles_received, articles_posted, articles_not_posted)
	images_not_uploaded = ""


def init(form_data):

	# login to the website. If login fails return error , else start processing

	if not form_data["website"].endswith("/"):
		form_data["website"] = form_data["website"] + u"/"

	session = login(form_data["website"], form_data["user_name"], form_data["password"])
	if session:
		start_processing(form_data, session)
	else:
		print "Login failed. Website: %s" % (form_data["website"])
