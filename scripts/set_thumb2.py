from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
creds = Credentials.from_authorized_user_file('/home/neilh/youtube-tool/token.json')
yt = build('youtube', 'v3', credentials=creds)
yt.thumbnails().set(videoId='TOX3foVXTJA', media_body=MediaFileUpload('/home/neilh/prime_video/thumbs/thumb_2.png', mimetype='image/png')).execute()
print('thumbnail 2 set on TOX3foVXTJA')
