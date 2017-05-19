from download_article import article_download
from edit_article import start_editing
from mediahandler import download_and_upload_images
from new_post import create_new_post
from post_it import post_article
from remove_everything import remove_files
from mailer import mail_the_report

import requests
import json

def login(webiste, user_name, password):

	if webiste and user_name and password:
		data = {'log': user_name, 'pwd': password}
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'}
		try:
			session = requests.Session()
			webiste = webiste + "wp-login.php"
			r = session.post(webiste, data=data, headers=headers)
		except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.exceptions.RequestException) as e:
			return False

		if r.status_code == requests.codes.ok:
			return session

	return False


def prepare_artilce_report(website, article_link, articles_report,posted):

    report = {"website": website, "article_link": article_link, "posted": posted}

    if posted:

        images_not_uploaded = []

        with open("../images_not_uploaded.txt", "r") as file_obj:
            images_not_uploaded.append(file_obj.readline())

        report["images_not_uploaded"] = images_not_uploaded

    articles_report.append(report)

    return articles_report




def start_processing(form_data, session):

	articles = form_data["articles"]
	website = form_data["website"]
	articles_report = []
	articles_received = 0
	articles_posted = 0
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
								articles_report = prepare_artilce_report(website, article_link, articles_report, True)
							else:
								articles_report = prepare_artilce_report(website, article_link, articles_report, False)

					else:
						articles_report = prepare_artilce_report(website, article_link, articles_report, False)

				else:
					articles_report = prepare_artilce_report(website, article_link, articles_report, False)
			else:
                                articles_report = prepare_artilce_report(website, article_link, articles_report, False)

			# remove all the files irrespective of whether the article got posted or not
			remove_files()

        mail_the_report(articles_report, articles_received, articles_posted)


def init(form_data):
	# login to the website. If login fails return error , else start processing
	if not form_data["website"].endswith("/"):
		form_data["website"] = form_data["website"] + "/"

	session = login(form_data["website"], form_data["user_name"], form_data["password"])
	if session:
		start_processing(form_data, session)
	else:
		print "Login failed. Website: %s" % (form_data["website"])
