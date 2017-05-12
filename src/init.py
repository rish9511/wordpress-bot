from download_article import article_download
from edit_article import start_editing
from mediahandler import download_and_upload_images
from new_post import create_new_post
from post_it import post_article
from remove_everything import remove_files
import requests


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


def start_processing(form_data, session):

	articles = form_data["articles"]
	for article_link in articles:
		if article_link:
			downloaded = article_download(article_link)
			if downloaded:
				edit_done = start_editing(form_data["tag"])
				if edit_done:
					post_created = create_new_post(session, form_data["website"])
					if post_created:

						if download_and_upload_images(session, form_data["website"]):  # the function always returns true, hence we don't have an else block
							if post_article(session, form_data["website"]):

								print "\nSuccess"
							else:
								print "\nFailed"

					else:
						print "\nCould not create the post %s " % (article_link)

				else:
					print "\nCould not edit the artilce %s " % (article_link)
			else:
				print "\nCould not Download the article %s " % (article_link)

			# remove all the files irrespective of whether the article got posted or not
			remove_files()


def init(form_data):
	# login to the website. If login fails return error , else start processing
	if not form_data["website"].endswith("/"):
		form_data["website"] = form_data["website"] + "/"

	session = login(form_data["website"], form_data["user_name"], form_data["password"])
	if session:
		start_processing(form_data, session)
	else:
		print "Login failed"
