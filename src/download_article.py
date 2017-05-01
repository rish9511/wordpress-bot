import httplib2
import os
import io

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = '~/google_oauth2/client_secret.json'
APPLICATION_NAME = 'article_downloader'


def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'article_dowloader.json')

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


def artilce_download():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)

    # download the article
    file_id = '1cg8FP3y1MlWtdOSN0hynEkv59FDMndnoBvXCJEywEhw'
    request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

        print("Download %d%%." % int(status.progress() * 100))
        if done:
            with open("../article.txt", "w") as file:
                file.write(fh.getvalue())
    return done
