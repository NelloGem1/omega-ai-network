from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/home/neilh/youtube-tool/token.json')
yt = build('youtube', 'v3', credentials=creds)
ch = yt.channels().list(part='snippet,statistics', mine=True).execute()
for c in ch['items']:
    print(c['snippet']['title'], '|', c['snippet']['customUrl'], '|', c['id'])
    print('subs:', c['statistics'].get('subscriberCount'))
