from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/home/neilh/youtube-tool/token.json')
yt = build('youtube', 'v3', credentials=creds)
yt.videos().delete(id='lUZ6T5jJRPU').execute()
print('old video deleted')
