import requests
from os import path
from getpass import getpass
import yt_dlp
from yt_dlp.networking import exceptions
# Links for Testing
# https://www.youtube.com/watch?v=D5kGXI8vUKg
# https://www.youtube.com/watch?v=udNXMAflbU8
# https://www.youtube.com/watch?v=ApYbwdFWytE

# Ensure both ffmpeg & yt_dlp is added to PATH
# Alternatively, add them to the same directory as this script
# Otherwise, change the filepath for the argument 'ffmpeg_location'
PROXY = 'gateway.atcnq.local:3128'
HOME_DIR = path.expanduser('~')

def main():
    check_options = {
        'ffmpeg_location': f'./ffmpeg',
        'quiet': True,
    }
    download_options = {
        'ffmpeg_location': f'./ffmpeg',
        'format': format_selector,
    }

    use_proxy = input('Require proxy credentials? (Y/n)').lower()
    if use_proxy in ['y', '']:
        print('\n-- Proxy Authentication --')
        username = input('Username: ')
        password = getpass()
        while check_proxy(username, password) == False:
            print('Invalid proxy credentials\n')
            username = input('Username: ')
            password = getpass()
        check_options['proxy'] = f'http://{username}:{password}@{PROXY}'
        download_options['proxy'] = f'http://{username}:{password}@{PROXY}'

    url = input('\nURLS - Enter each YouTube URL one at a time, enter nothing to finish\n>> ')
    titles = []
    videos = []

    while url != '':
        if url[:43] in videos:
            print('Video already added')
        elif 'youtube.com' in url or 'youtu.be' in url:
            try:
                titles.append(get_title(url, check_options))
                videos.append(url)
            except yt_dlp.utils.DownloadError:
                print('Verification error: Check video URL')
            except exceptions.NoSupportingHandlers:
                print('Verification error: Check video URL')
        else:
            print('Invalid URL')
        url = input('>> ')
    edit_videos(check_options, titles, videos)

    final_directory = get_directory()
    download_options['paths'] = {'home': f'{final_directory}', 'temp': HOME_DIR}
    # yt_dlp.YoutubeDL arguments for proxy auth, ffmpeg binary & forcing good codecs

    try: 
        print('----- DOWNLOAD STARTED -----')
        with yt_dlp.YoutubeDL(download_options) as ydl:
            ydl.download(videos)
    except yt_dlp.utils.DownloadError:
        print('\nDownload Error occured: Notify William')
        
def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if 'avc1' in f['vcodec'] and f['ext'] != 'webm' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a'}[best_video['ext']]
    # vcodec='none' means there is no videoa
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

def get_title(url, options):
    try: 
        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            return video_title
    except yt_dlp.utils.DownloadError:
        raise yt_dlp.utils.DownloadError('Check video URL')
    
def display_videos(titles):
    print('\nThese are the videos in your list:')
    # List titles to user
    for i, title in enumerate(titles):
        print(f'{i+1}. {title}')

def edit_videos(check_options, titles, videos):
    display_videos(titles)
    # Provide option to change or clear entire list
    # is_editing = input('\nWould you like to edit the list? (Y/N)\n>> ').lower()
    choice = input('\nWould you like to (A)dd to or (E)dit the list, Enter nothing to skip\n>> ').lower()
    while choice != '':
        while choice not in ['a', 'e']:
            print('Invalid input')
            choice = input('\nWould you like to (A)dd to or (E)dit the list, Enter nothing to skip\n>> ').lower()
        if choice == 'a':
            new_url = input('\nPlease enter the new YouTube URL\n>> ')
            if 'youtube.com' in new_url or 'youtu.be' in new_url:
                try:
                    titles.append(get_title(new_url, check_options))
                    videos.append(new_url)
                except yt_dlp.utils.DownloadError:
                    print('Verification error: Check video URL')
            else:
                print('Invalid link')
        if choice == 'e':
            # Change singular list elements by having index's in the provided list
            video_number = get_number('\nPlease enter the video number you wish to change\n>> ')
            while video_number > len(titles):
                print('Invalid video number')
                video_number = get_number('\nPlease enter the video number you wish to change\n>> ')

            verified = False
            while not verified:
                new_url = input('\nPlease enter the new YouTube URL\n>> ')
                if 'youtube.com' in new_url or 'youtu.be' in new_url:
                    try:
                        titles[video_number - 1] = get_title(new_url, check_options)
                        videos[video_number - 1] = new_url
                        verified = True
                    except yt_dlp.utils.DownloadError:
                        print('Verification error: Check video URL')
                else:
                    print('Invalid link')
        display_videos(titles)
        choice = input('\nWould you like to (A)dd to or (E)dit the list, Enter nothing to skip\n>> ').lower()


def get_number(prompt):
    value = input(prompt)
    while type(value) == str:
        try:
            value = int(value)
        except ValueError:
            print('Invalid input')
            value = input(prompt)
    return value

def check_proxy(username, password):
    proxies = {'https': f'http://{username}:{password}@{PROXY}'}
    try:
        r = requests.get('https://youtube.com', proxies=proxies)
        if r.status_code == 200:
            return True
        return False
    except requests.exceptions.ProxyError :
        return False
    
def get_directory():
    dir = input('\nEnter your desired download location - Desktop by default\n>> ')
    while path.isdir(dir) == False:
        if dir == '':
            return f'{HOME_DIR}/Desktop'
        print('Invalid directory')
        dir = input('\nEnter your desired download location - Desktop by default\n>> ')
    return dir

main()
