import webbrowser
import subprocess
import locale
import download_thread
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

locale.setlocale(locale.LC_ALL, '')


class YouTubeClient:
    
    DEVELOPER_KEY = 'AIzaSyDbzki3busW9XM2cOGIn1ciVXXuo_nEIkU'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    def __init__(self):
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
            developerKey=self.DEVELOPER_KEY)
        self.max_results = 25
        self.last_search = None

    def search(self, search_terms, page=1):

        search_response = self.youtube.search().list(
            q=search_terms,
            part='id,snippet',
            maxResults=self.max_results,
            type="video"
        ).execute()
        
        videos = []

        try:
            videos = self.get_videos(search_response)
        except:
            videos = []
        
        """ 
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                video_title = search_result["snippet"]["title"]
                video_id = search_result["id"]["videoId"]
                videos.append("{} {}".format(video_title, video_id)) 
        """
        return videos

    def get_videos(self, search_response):
        #@@seb Rewrite YoutubeVideo class
        videos = []
        
        for search_result in search_response.get('items', []):
            #if search_result['id']['kind'] == "youtube#video":
            new_video = YouTubeVideo(search_result)
            videos.append(new_video)
 
        """
        for entry in feed.entry:
            new_video = YouTubeVideo(entry)
            videos.append(new_video)
        """
        return videos

    def next_page(self):
        return self.search(self.last_search[0], self.last_search[1] + 1)

    def get_local_video(self, video_title):
        # replace html code &#47; with slashes
        video_title = video_title.replace('&#47;', '/')
        title = gdata.media.Title(text=video_title)
        group = gdata.media.Group(title=title)
        video_entry = gdata.youtube.YouTubeVideoEntry(media=group)
        return YouTubeVideo(video_entry)


class YouTubeVideo:
    downloads = []

    def __init__(self, entry):
        self.entry = entry
        self.title = entry["snippet"]["title"]
        self.download_process = None

        # replace slashes with html code &#47;
        self.filename = self.title.replace('/', '&#47;')

        try:
            self.url = "https://www.youtube.com/watch?v={}".format(self.entry["id"]["videoId"])
            self.description = self.entry["snippet"]["description"]
            self.author = "not done yet"
            self.published = d["snippet"]["publishTime"]
        except:
            # dunno, local video
            self.author = 'N/A'
            self.published = 'N/A'

        try:
            # duration todo 
            self.duration = "00:00:00"
            self.duration = self.get_formatted_duration()
        except AttributeError:
            self.duration = 'N/A'

        try:
            #self.views = entry.statistics.view_count
            #self.views = self.get_formatted_views()
            self.views = "0"
        except AttributeError:
            self.views = 'N/A'

        try:
            #self.rating = entry.rating.average
            #self.rating = str(round(float(self.rating), 1))
            self.rating = "0"
        except AttributeError:
            self.rating = 'N/A'

    def open(self):
        webbrowser.open_new_tab(self.url)

    def download(self):
        self.dl = download_thread.DownloadThread(self.filename, self.url)
        self.dl.start()
        YouTubeVideo.downloads.append(self)

    def abort(self):
        try:
            self.dl.kill()
            return 'Aborted downloading "' + self.title + '"'
        except:
            return 'Aborting downloading "' + self.title + '" failed'

    def get_formatted_duration(self):
        #m, s = divmod(int(self.duration), 60)
        #h, m = divmod(m, 60)
        #formatted_duration = "%d:%02d:%02d" % (h, m, s)
        #return formatted_duration
        #todo 
        return "00:00:00"

    def get_formatted_views(self):
        return locale.format('%d', int(self.views), grouping=True)

    def play(self):
        devnull = open(os.devnull)
        extensions = ['.flv', '.mp4', '.webm', '.mkv']
        for ext in extensions:
            file = self.filename + ext
            if os.path.exists(file):
                subprocess.Popen(['mplayer', '-msglevel', 'all=-1', '-use-filename-title', file], stdin=devnull)
                return True
        return False

    def stream(self):
        #cookie = '/tmp/videotop_cookie'
        #c1 = ['youtube-dl', '--get-url', '--cookies=' + cookie, self.url]
        #stream = subprocess.check_output(c1).strip()
        #c2 = ['mplayer', '-msgcolor', '-title', self.title, '-prefer-ipv4', '-cookies', '-cookies-file', cookie, stream]
        #subprocess.call(c2)
        cli = ['mpv', '-ytdl-format=bestvideo+bestaudio', self.url]
        subprocess.call(cli)

