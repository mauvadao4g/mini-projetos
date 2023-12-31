import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DATA_DIR = "data"

def get_comment_replies(youtube, parent_id):
    "Retorna lista de respostas a um comentario"

    replies = []
    try:
        response = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            maxResults=100,
            textFormat="plainText"
        ).execute()
        for element in response["items"]:
            replies.append(element["snippet"]["textDisplay"])

    except HttpError as e:
        print(e)
    return replies

def save_video_comments(youtube, video_id, filename):
    "Salva comentarios de um video em um arquivo"

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    try:
        response = request.execute()
        has_next = True
        page_idx = 0
        while has_next:
            page_idx += 1
            print(f"Page: {page_idx}")
            comments = []
            for item in response["items"]:
                snippet = item["snippet"]
                comment = snippet["topLevelComment"]
                text = comment["snippet"]["textDisplay"]
                comments.append(text)
                # Pegar respostas tambem!
                if snippet["totalReplyCount"] > 0:
                    # print(text), se quiser ter um feedback
                    replies = get_comment_replies(youtube, comment["id"])
                    comments.extend(replies)
            
            with open(os.path.join(DATA_DIR, filename), "a") as savefile:
                savefile.write("\n".join(comments))

            if "nextPageToken" in response:
                token = response["nextPageToken"]
                response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=token
                ).execute()
            else:
                has_next = False

    except HttpError as e:
        print(e)


def count_hashtag(comments, hashtag):
    counter = 0
    for comment in comments:
        if hashtag in comment.lower():
            counter += 1
    return counter

if __name__ == '__main__':
    with open("apikey.txt") as apifile:
        api_key = apifile.read().strip()
    api_name = "youtube"
    api_version = "v3"
    video_id = "BRPUA0EgS4I" #"Td-La4kF-Lo"
    filename = "sql.txt"
    hashtag = "#sql"

    youtube = build(api_name, api_version, developerKey=api_key)

    save_video_comments(youtube, video_id, filename)

    with open(os.path.join(DATA_DIR, filename)) as commentsfile:
        comments = commentsfile.readlines()
    
    found = count_hashtag(comments, hashtag)
    print(f"Total de comentários: {len(comments)}\nCom {hashtag}: {found}")
