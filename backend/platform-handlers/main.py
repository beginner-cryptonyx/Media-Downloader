import subprocess
import json
from exceptions import InvalidLinkError, ModuleError

class LinkHandler():
    def __init__(self, link:str):
        self.link = link
        self.metadata = None
        self.get_metadata()


    def get_metadata(self):
        metadata = subprocess.run(["yt-dlp", "-j", self.link], capture_output=True, text=True)
        
        if metadata.returncode != 0:
            raise InvalidLinkError(f"Could not fetch video info: {metadata.stderr.strip()}")

        try: 
            self.metadata = json.loads(metadata.stdout)
        except json.JSONDecodeError:
            raise InvalidLinkError("Received unexpected response for this link")
        

    def get_display_info(self):
        if self.metadata is not None:
            info = {
                'id': self.metadata['id'],
                'title': self.metadata['title'],
                'duration': self.metadata['duration'],
                'views': self.metadata['view_count'],

            }
            return info
        else: raise ModuleError("Something went wrong, unable to fetch metadata")
    
    def get_streams(self):
        if self.metadata is None:
            raise ModuleError("Something went wrong, unable to fetch metadata")
        self.audio_info = {}
        self.video_info = {}
        for stream in self.metadata["formats"]:
            if stream['format_note'] != 'storyboard':
                if stream["vcodec"] == 'none':
                    self.audio_info[stream["format_id"]] = {
                        "note": stream["format_note"],
                        "file_ext": stream['ext'],
                        "size": stream.get("filesize_approx") or 0,
                        "avg_bitrate": stream.get("abr") or 0
                    }
                else:
                    self.video_info[stream["format_id"]] = {
                        "note": stream["format_note"],
                        "file_ext": stream['ext'],
                        "size": stream.get("filesize_approx") or 0,
                        'fps': stream['fps']
                    }
        return self.video_info, self.audio_info
    
    def download_content(self, video_id):
        sorted_audio = dict(sorted(self.audio_info.items(), key=lambda item: item[1]["avg_bitrate"], reverse=True))
        subprocess.run(["yt-dlp", "-f", f"{video_id}+{next(iter(sorted_audio))}", self.link])
        


if __name__ == "__main__":
    handler = LinkHandler("https://youtu.be/x-wf8Yb5ZCM?si=u1ZWtQc85v1WCFH7") # Khabib by Central Cee
    print(handler.get_display_info())
    print(handler.get_streams()[0])
    id = input("choose an id")
    handler.download_content(id)
