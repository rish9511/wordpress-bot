# -*- coding: UTF-8 -*-
import httplib2
import os
import io
import re

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = '~/google_oauth2/client_secret.json'
APPLICATION_NAME = 'article_downloader'


def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'article_downloader.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_article_id(article_link):

    pattern = u"https://docs.google.com/document/d/(.*)/"
    try:
        if re.search(pattern, article_link):
            return re.search(pattern, article_link).group(1)
    except (re.error, IndexError) as e:
        return None


def download(article_id, google_service):

    try:
        request = google_service.files().export_media(fileId=article_id, mimeType='text/plain')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if done:
                with open("../article.txt", "w") as file:
                    try:
                        # store the article as bytes of strings with character encoding as utf-8
                        article = fh.getvalue().decode('utf-8', errors='ignore').encode('utf-8', errors='ignore')
                        file.write(article)
                    except (UnicodeDecodeError, UnicodeEncodeError) as e:
                        # failed to convert the downloaded article's encoding to utf-8. storing the article as received
                        file.write(fh.getvalue())

        return done
    except Exception:
        return False


def article_download(article_link):
    '''
        * step 1 - get the credentials and authenticate
        * step 2 - get the article id from the article_link
        * step 3 - download
    '''
    try:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        google_service = discovery.build('drive', 'v2', http=http)

        article_id = get_article_id(article_link)

        if article_id:
            if download(article_id, google_service):
                return True

        return False
    except Exception as e:
        return False
