import sys
import json
from yt_dlp import YoutubeDL

def download_audio_segment(video_url, start_time=None, end_time=None, output_file_name=None):
    # Set default start time to 0 if not provided
    start_time = start_time or 0
    # Convert start and end times from seconds to hh:mm:ss format
    start_time_hms = str(int(start_time) // 3600).zfill(2) + ':' + str((int(start_time) % 3600) // 60).zfill(2) + ':' + str(int(start_time) % 60).zfill(2)
    
    # Set up yt-dlp options to get video info for end_time and output_file_name
    ydl_opts_info = {
        'format': 'bestaudio',
    }
    
    # Get video info
    with YoutubeDL(ydl_opts_info) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', 'video')
        # Set default end time to video duration if not provided
        end_time = end_time or info_dict.get('duration')
        # Convert end time to hh:mm:ss format
        end_time_hms = str(int(end_time) // 3600).zfill(2) + ':' + str((int(end_time) % 3600) // 60).zfill(2) + ':' + str(int(end_time) % 60).zfill(2)
        # Set default output file name if not provided
        if not output_file_name:
            output_file_name = f"[{start_time}-{end_time}] - {video_title}"

    # Set up yt-dlp options for audio download
    ydl_opts_download = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'external_downloader': 'ffmpeg',
        'external_downloader_args': ['-ss', start_time_hms, '-to', end_time_hms],
        'outtmpl': output_file_name,
    }

    # Download the audio using yt-dlp
    with YoutubeDL(ydl_opts_download) as ydl:
        ydl.download([video_url])

    # Write metadata to a JSON file
    json_file_name = output_file_name.rsplit('.', 1)[0] + '.json'
    with open(json_file_name, 'w', encoding='utf-8') as f:
        json.dump(info_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Command line arguments
    video_url = sys.argv[1]
    start_time_seconds = sys.argv[2] if len(sys.argv) > 2 else None
    end_time_seconds = sys.argv[3] if len(sys.argv) > 3 else None
    output_file_name = sys.argv[4] if len(sys.argv) > 4 else None

    download_audio_segment(video_url, start_time_seconds, end_time_seconds, output_file_name)
