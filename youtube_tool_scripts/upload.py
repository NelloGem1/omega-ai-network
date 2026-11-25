"""Upload a video: python upload.py <video_file> --title "..." --description "..." """
import argparse
from googleapiclient.http import MediaFileUpload
from youtube_api import get_service


def upload_video(path, title, description, tags=None, privacy="unlisted"):
    svc = get_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": privacy,   # private | unlisted | public
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(path, chunksize=-1, resumable=True)
    req = svc.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = req.next_chunk()
        if response:
            print(f"Uploaded: https://youtu.be/{response['id']}")
    return response


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--privacy", default="unlisted",
                   choices=["private", "unlisted", "public"])
    args = p.parse_args()
    upload_video(
        args.video,
        args.title,
        args.description,
        tags=[t.strip() for t in args.tags.split(",") if t.strip()],
        privacy=args.privacy,
    )
