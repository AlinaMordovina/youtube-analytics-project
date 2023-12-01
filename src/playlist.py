import datetime
import os
from googleapiclient.discovery import build
import isodate


class PlayList:

    api_key: str = os.getenv('YT_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    def __init__(self, playlist_id):

        self.playlist_id = playlist_id
        self._playlist = self.youtube.playlists().list(id=self.playlist_id, part='snippet,contentDetails',
                                                       maxResults=50).execute()
        self.title = self._playlist['items'][0]['snippet']['title']
        self.url = f"https://www.youtube.com/playlist?list={self.playlist_id}"
        self._playlist_videos = self.youtube.playlistItems().list(playlistId=self.playlist_id, part='contentDetails',
                                                                  maxResults=50).execute()
        self._video_ids: list[str] = [video['contentDetails']['videoId'] for video in self._playlist_videos['items']]
        self._video_response = (self.youtube.videos().list(part='contentDetails,statistics',
                                                           id=','.join(self._video_ids)).execute())

    @property
    def total_duration(self):
        duration = datetime.timedelta(hours=0, minutes=0, seconds=0)

        for video in self._video_response['items']:
            # YouTube video duration is in ISO 8601 format
            iso_8601_duration = video['contentDetails']['duration']
            duration_video = isodate.parse_duration(iso_8601_duration)
            duration += duration_video

        return duration

    def show_best_video(self):
        most_like = 0
        video_id_with_most_like = ''

        for video in self._video_response['items']:
            if int(video['statistics']['likeCount']) > most_like:
                most_like = int(video['statistics']['likeCount'])
                video_id_with_most_like = video['id']
            else:
                continue

        return f"https://youtu.be/{video_id_with_most_like}"
