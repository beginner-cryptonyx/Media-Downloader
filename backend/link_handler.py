import subprocess
import json

class LinkHandler():
    def __init__(self, link:str):
        self.link = link
    def get_metadata(self):
        metadata = subprocess.run(["yt-dlp", "-j", self.link], capture_output=True, text=True)
        metadata = json.loads(metadata.stdout)
        self.metadata = metadata
    def get_display_info(self):
        info = {
            'id': self.metadata['id'],
            'title': self.metadata['title'],
            'duration': self.metadata['duration'],
            'views': self.metadata['view_count'],
            # 'id': formats['id'],
            # 'id': formats['id'],
            # 'id': formats['id'],
        }
        return info
    

    def get_formats(self):
        formats = self.metadata["formats"]
        return formats


if __name__ == "__main__":
    handler = LinkHandler("https://youtu.be/x-wf8Yb5ZCM?si=u1ZWtQc85v1WCFH7") # Khabib by Central Cee
    handler.get_metadata()
    print(handler.get_display_info())
    print(handler.get_formats())
