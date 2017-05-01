import dowload_article
import edit_article
import mediahandler
import new_post
import post_it

form_data = {}


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


def start_processing(session):
	# step1
	# dowload the article
	downloaded = article_download()
	if downloaded:
		edit_done = start_editing()
		if edit_done:
			post_created = create_new_post(session)
			if post_created:
				dl_ul_done = download_and_upload_images()
				if dl_ul_done:
					posted = start_posting()


def init():
	# login to the website. If login fails return error , else start processing
	session = login()
	if session:
		start_processing(session)
	else:
		print "Login failed"