from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/home/neilh/youtube-tool/token.json')
yt = build('youtube', 'v3', credentials=creds)
v = yt.videos().list(part='snippet,status', id='TOX3foVXTJA').execute()['items'][0]
print('TITLE:', v['snippet']['title'])
print('TAGS:', v['snippet'].get('tags'))
print('---DESC---')
print(v['snippet']['description'][-600:])
print('privacy:', v['status']['privacyStatus'])
