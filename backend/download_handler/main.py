import subprocess
import json
import re
import os
from exceptions import InvalidLinkError, ModuleError, DownloadError

class LinkHandler():
    """
    Handles fetching metadata and downloading video from an URL

    Attributes:
        link (str): URL of the video
    """
    def __init__(self, link:str):
        """initiallise the class

        Args:
            link (str): Link from which to fetch the metadata
        """
        self.link = link
        self.metadata = None
        self.audio_info = None
        self.video_info = None
        self.get_metadata()


    def get_metadata(self):
        """Gets meta data from video, including title, duration, and views

        Raises:
            InvalidLinkError: If metadata could not be fetched
            InvalidLinkError: If metadata could not be decoded
        """
        metadata = subprocess.run(["yt-dlp", "-j", self.link], capture_output=True, text=True)
        
        if metadata.returncode != 0:
            raise InvalidLinkError(f"Could not fetch video info: {metadata.stderr.strip()}")

        try: 
            self.metadata = json.loads(metadata.stdout)
        except json.JSONDecodeError:
            raise InvalidLinkError("Received unexpected response for this link")
        

    def get_display_info(self):
        """From metadata it returns the id, views, title, duration, and view count in a dict

        Raises:
            ModuleError: If self.metadata is empty

        Returns:
            dict[str,any]: The return object of all information to be displayed to user
        """
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
        """Gets the audio and video streams from video URL

        Raises:
            ModuleError: if metadata is empty

        Returns:
            tuple[dict, dict]: (video_info, audio_info) where both dicts are keyed by ids 
        """
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
    
    def download_content(self, video_id, output_path=None):
        """Method to download a video form the URL based on the video stream ID provided

        Args:
            video_id (str): Video ID from the return value of the first element of the get_streams() tuple
            output_path (string, optional): A pre-existing path to which the downloaded video is saved to. Defaults to None.

        Raises:
            ModuleError: If the audio_info is empty
            ValueError: If path doesn't exist
            ValueError: Not enough permission to access given path
            DownloadError: If download fails
        """
        if not self.audio_info:
            raise ModuleError("could not get audio streams (was the get_streams() method used?)")
        sorted_audio = dict(sorted(self.audio_info.items(), key=lambda item: item[1]["avg_bitrate"], reverse=True))
        command = ["yt-dlp", "-f", f"{video_id}+{next(iter(sorted_audio))}"]

        if output_path is not None:
            if not os.path.isdir(output_path):
                raise ValueError(f"Output path does not exist: {output_path}")
            if not os.access(output_path, os.W_OK):
                raise ValueError(f"No write permission for path: {output_path}")
            
            command.append('-o')
            command.append(f"{output_path}/%(title)s [%(id)s].%(ext)s")

        command.append(self.link)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 0: not started, 1: video, 2: audio
        phase = 0 
        for line in process.stdout:
            line = line.strip()
            if "Destination:" in line:
                phase += 1
            if "[download]" in line:
                # print(line)
                match_object = re.search(r"\d+\.\d+(?=%)", line)
                if match_object is not None:
                    if phase == 1:
                        yield float(match_object.group())/2, '%'
                    elif phase == 2:
                        yield float(match_object.group())/2+50, '%'

        process.wait()
        if process.returncode != 0:
            raise DownloadError("Unable to download video")
        


if __name__ == "__main__":
    handler = LinkHandler("https://youtu.be/x-wf8Yb5ZCM?si=u1ZWtQc85v1WCFH7") # Khabib by Central Cee
    print(handler.get_display_info())
    print(handler.get_streams()[0])
    id = input("choose an id")
    handler.download_content(id, "./output")
