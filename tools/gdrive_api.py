from __future__ import absolute_import, unicode_literals

import os

import httplib2
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

HOMEDIR = os.path.expanduser('~')

CLIENT_ID_FILE = os.path.join(HOMEDIR, 'gdrive_client_id')
CLIENT_SECRET_FILE = os.path.join(HOMEDIR, 'gdrive_client_secret')

# Copy your credentials from the console
CLIENT_ID = None
CLIENT_SECRET = None
SECRETS_INITIALIZED = False


def ensure_secrets():
    global SECRETS_INITIALIZED
    if SECRETS_INITIALIZED:
        return

    with codecs.open(CLIENT_ID_FILE, 'r', 'utf8') as f:
        global CLIENT_ID
        CLIENT_ID = f.read().strip()

    with codecs.open(CLIENT_SECRET_FILE, 'r', 'utf8') as f:
        global CLIENT_SECRET
        CLIENT_SECRET = f.read().strip()

    SECRETS_INITIALIZED = True


def get_credentials():
    credentials_file = os.path.join(HOMEDIR, 'gdrive_creds')
    storage = Storage(credentials_file)
    creds = storage.get()
    if creds:
        return creds

    # first, make sure we grabbed the credentials
    ensure_secrets()

    OAUTH_SCOPE = ' '.join((
        'https://www.googleapis.com/auth/drive',
        'https://spreadsheets.google.com/feeds',
    ))

    # Redirect URI for installed apps
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE,
                               redirect_uri=REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
    return storage.get()


def get_service():
    credentials = get_credentials()

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    return build('drive', 'v2', http=http)
