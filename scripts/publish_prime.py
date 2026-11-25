from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/home/neilh/youtube-tool/token.json')
yt = build('youtube', 'v3', credentials=creds)
res = yt.videos().update(part='status', body={'id': 'TOX3foVXTJA', 'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}).execute()
print('privacyStatus:', res['status']['privacyStatus'])
print('URL: https://youtu.be/TOX3foVXTJA')
