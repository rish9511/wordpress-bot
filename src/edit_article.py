# -*- coding: UTF-8 -*-
import os
import re


def replace_original_with_temp(temp_file, original_file):

	move = 'mv %s %s' % (temp_file, original_file)
	try:
		os.system(move)
	except OSError as e:
		return False

	return True


def write_to_temp_file(text):

	try:
		text = text.encode('utf-8', errors='ignore')
	except (UnicodeDecodeError, UnicodeEncodeError) as e:
		# failed to convert the text to str type before writing to temp file
		pass

	try:
		with open("../article.txt.tmp", "a") as temp_article:
			temp_article.write(text)
	except IOError as error:
		# this is just bad. If it ever happens, the artilce will be incomplete.
		return False

	return True


def edit_article(tag):

	try:
		with open("../article.txt", "r") as article:
			title_found = False
			product_link_found = False
			price_tag_link = u""
			for line in article:
				try:
					line = line.decode('utf-8', errors='ignore')
				except (UnicodeDecodeError, UnicodeEncodeError) as e:
					pass

				if line.strip() != "":
					if not title_found:
						line = "00" + line + "\n"
						write_to_temp_file(line)
						title_found = True

					elif u"https://" in line or u"http://" in line or u"www.amazon.com" in line:
						link = re.search(u"(.*/dp/\w*/?)", line)
						if link:
							link = link.group(1)
							if link[-1:] == "/":
								link = link[:-1]
							link = link + u"?tag=%s" % (tag)

						if price_tag_link:
							price_tag_link = "05" + price_tag_link + "\n"
							write_to_temp_file(price_tag_link)

						if link:
							price_tag_link = link
							line = "07" + link + "\n"
						else:
							price_tag_link = line
							line = "07" + line + "\n"

						write_to_temp_file(line)
						product_link_found = True

					elif product_link_found:
						line = "02" + line + "\n06\n"
						write_to_temp_file(line)
						product_link_found = False

					elif "Conclusion" in line:
						if price_tag_link:
							price_tag_link = "05" + price_tag_link + "\n"
							write_to_temp_file(price_tag_link)
						line = "08" + line + "\n"
						write_to_temp_file(line)

					elif len(line) > 100:
						line = "01" + line + "\n"
						write_to_temp_file(line)

	except (IOError, UnicodeDecodeError, UnicodeEncodeError, re.error, IndexError) as error:
		return False

	return True


def start_editing(tag):

	if edit_article(tag):
		if replace_original_with_temp("../article.txt.tmp", "../article.txt"):
			return True

	return False
