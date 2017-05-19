import os


def remove_files():
	try:
		os.system('rm  ../*.jpg')
		os.system('rm ../article_details.txt')
		os.system('rm ../id.txt')
		os.system('rm ../article.txt')
		os.system('rm ../images_not_uploaded.txt')
	except OSError as e:
		pass
