from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/home/neilh/youtube-tool/token.json')
yt = build('youtube', 'v3', credentials=creds)
v = yt.videos().list(part='snippet', id='TOX3foVXTJA').execute()['items'][0]
desc = v['snippet']['description']
# replace trailing hashtag line with approved set
lines = desc.rstrip().split('\n')
while lines and lines[-1].strip().startswith('#'):
    lines.pop()
desc = '\n'.join(lines) + '\n\n#PrimeNumbers #Mathematics #Lean4 #TheoremProving #NumberTheory #Math #Verified #Discovery #Philippines #STEM'
body = {'id': 'TOX3foVXTJA', 'snippet': {'title': v['snippet']['title'], 'description': desc, 'categoryId': v['snippet']['categoryId'], 'tags': v['snippet'].get('tags', [])}}
yt.videos().update(part='snippet', body=body).execute()
print('description updated')
print(desc[-200:])
